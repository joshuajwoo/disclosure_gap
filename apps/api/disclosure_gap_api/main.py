from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import Engine, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import Settings, get_settings
from .contract_versions import UnsupportedContractVersionError, validate_check_in
from .database import build_engine, session_scope
from .models import (
    Assessment,
    BaselineContext,
    CheckIn,
    ConsentEvent,
    Participant,
    StudyEvent,
)
from .schemas import AssessmentSubmission as AssessmentPayload
from .schemas import (
    BaselineContextSubmission,
    DeletionResponse,
    EnrollmentRequest,
    EnrollmentResponse,
    RecoveryRequest,
    SessionResponse,
    SubmissionResponse,
    TrendsResponse,
)
from .security import (
    hash_recovery_code,
    hash_session_token,
    new_recovery_code,
    new_session_token,
    verify_recovery_code,
)

logger = logging.getLogger("disclosure_gap_api")


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def utcnow() -> datetime:
    return datetime.now(UTC)


def canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def score_assessment(payload: AssessmentPayload) -> int | None:
    numeric = [
        item.response_code for item in payload.responses if isinstance(item.response_code, int)
    ]
    if len(numeric) <= 7:
        return None
    if len(numeric) == 10:
        return sum(numeric)
    return math.floor((sum(numeric) * 10 / len(numeric)) + 0.5)


def normalized_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def assert_submission_window(
    participant: Participant,
    now: datetime,
    *,
    assessment_type: str | None = None,
    week: int | None = None,
    enforce: bool,
) -> None:
    if not enforce:
        return
    enrolled = normalized_utc(participant.created_at)
    elapsed = now - enrolled
    if assessment_type == "baseline" and not timedelta(0) <= elapsed < timedelta(days=7):
        raise ApiError(409, "window_closed", "The baseline window is not open.")
    if assessment_type == "follow_up" and not timedelta(days=28) <= elapsed < timedelta(days=42):
        raise ApiError(409, "window_closed", "The follow-up window is not open.")
    if week is not None:
        start = timedelta(days=7 * (week - 1))
        if not start <= elapsed < start + timedelta(days=7):
            raise ApiError(409, "window_closed", "This check-in window is not open.")


def audit(
    session: Session,
    participant_id: str | None,
    event_type: str,
    route_code: str,
    result_code: str,
) -> None:
    session.add(
        StudyEvent(
            participant_id=participant_id,
            event_type=event_type,
            route_code=route_code,
            result_code=result_code,
        )
    )


def create_app(
    *,
    settings: Settings | None = None,
    engine: Engine | None = None,
    clock: Callable[[], datetime] = utcnow,
) -> FastAPI:
    active_settings = settings or get_settings()
    active_engine = engine or build_engine(active_settings.database_url)
    application = FastAPI(
        title="The Disclosure Gap API",
        version="1.0.0",
        docs_url="/docs" if active_settings.app_env != "production" else None,
        redoc_url=None,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[active_settings.web_origin],
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )

    def get_session() -> Iterator[Session]:
        yield from session_scope(active_engine)

    def current_participant(
        request: Request, session: Session = Depends(get_session)
    ) -> Participant:
        authorization = request.headers.get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise ApiError(401, "unauthorized", "A valid participant session is required.")
        participant = session.scalar(
            select(Participant).where(
                Participant.session_token_hash == hash_session_token(token),
                Participant.withdrawal_state == "active",
            )
        )
        if participant is None:
            raise ApiError(401, "unauthorized", "A valid participant session is required.")
        return participant

    @application.middleware("http")
    async def safe_request_log(request: Request, call_next: Any) -> Any:
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        logger.info(
            "request_complete method=%s path=%s status=%s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            request.state.request_id,
        )
        return response

    @application.exception_handler(ApiError)
    async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "requestId": getattr(request.state, "request_id", None),
                }
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, _error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "invalid_request",
                    "message": "The request does not match the expected contract.",
                    "requestId": getattr(request.state, "request_id", None),
                }
            },
        )

    @application.get("/health")
    def health(session: Session = Depends(get_session)) -> dict[str, str]:
        session.execute(select(1)).scalar_one()
        return {"status": "ok", "environment": active_settings.app_env}

    @application.post("/v1/participants", response_model=EnrollmentResponse, status_code=201)
    def enroll(
        payload: EnrollmentRequest, session: Session = Depends(get_session)
    ) -> EnrollmentResponse:
        if payload.age_band not in {"18_19", "20_22"}:
            raise ApiError(422, "not_eligible", "Enrollment is available only to eligible adults.")
        if (
            payload.consent_action != "agree"
            or payload.consent_version != active_settings.consent_version
        ):
            raise ApiError(422, "consent_required", "The current consent must be accepted.")

        token = new_session_token()
        recovery_code = new_recovery_code()
        participant = Participant(
            age_band=payload.age_band,
            contract_version=payload.contract_version,
            recovery_code_hash=hash_recovery_code(recovery_code),
            session_token_hash=hash_session_token(token),
            created_at=clock(),
        )
        session.add(participant)
        session.flush()
        session.add(
            ConsentEvent(
                participant_id=participant.id,
                consent_version=payload.consent_version,
                action="agree",
                occurred_at=clock(),
            )
        )
        audit(session, participant.id, "submission_accepted", "participants", "created")
        session.commit()
        return EnrollmentResponse(
            participantId=participant.id,
            sessionToken=token,
            recoveryCode=recovery_code,
            contractVersion=participant.contract_version,
        )

    @application.post("/v1/sessions/recover", response_model=SessionResponse)
    def recover(
        payload: RecoveryRequest, session: Session = Depends(get_session)
    ) -> SessionResponse:
        participant = session.get(Participant, payload.participant_id)
        if (
            participant is None
            or participant.withdrawal_state != "active"
            or participant.recovery_code_hash is None
            or not verify_recovery_code(payload.recovery_code, participant.recovery_code_hash)
        ):
            raise ApiError(401, "recovery_failed", "The recovery information was not accepted.")
        token = new_session_token()
        participant.session_token_hash = hash_session_token(token)
        audit(session, participant.id, "session_recovered", "sessions", "rotated")
        session.commit()
        return SessionResponse(sessionToken=token)

    @application.post("/v1/baseline-context", response_model=SubmissionResponse, status_code=201)
    def submit_baseline_context(
        raw_payload: dict[str, Any],
        participant: Participant = Depends(current_participant),
        session: Session = Depends(get_session),
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=64),
    ) -> SubmissionResponse | JSONResponse:
        try:
            payload = BaselineContextSubmission.model_validate(raw_payload)
        except ValidationError as error:
            audit(session, participant.id, "submission_rejected", "baseline_context", "contract")
            session.commit()
            raise ApiError(
                422, "invalid_contract", "The baseline context contract is invalid."
            ) from error
        payload_hash = canonical_hash(payload.model_dump(by_alias=True, mode="json"))
        existing = session.scalar(
            select(BaselineContext).where(BaselineContext.participant_id == participant.id)
        )
        if existing is not None:
            if (
                existing.idempotency_key == idempotency_key
                and existing.payload_hash == payload_hash
            ):
                return JSONResponse(
                    status_code=200,
                    content=SubmissionResponse(id=existing.id, status="replayed").model_dump(),
                )
            audit(session, participant.id, "submission_rejected", "baseline_context", "duplicate")
            session.commit()
            raise ApiError(409, "duplicate_submission", "Baseline context was already submitted.")
        try:
            assert_submission_window(
                participant,
                clock(),
                assessment_type="baseline",
                enforce=active_settings.enforce_study_windows,
            )
        except ApiError:
            audit(session, participant.id, "submission_rejected", "baseline_context", "window")
            session.commit()
            raise

        support = (
            payload.support_confidence if isinstance(payload.support_confidence, int) else None
        )
        support_nr = (
            payload.support_confidence if isinstance(payload.support_confidence, str) else None
        )
        everyday = payload.everyday_comfort if isinstance(payload.everyday_comfort, int) else None
        everyday_nr = (
            payload.everyday_comfort if isinstance(payload.everyday_comfort, str) else None
        )
        insecurity = (
            payload.insecurity_comfort if isinstance(payload.insecurity_comfort, int) else None
        )
        insecurity_nr = (
            payload.insecurity_comfort if isinstance(payload.insecurity_comfort, str) else None
        )
        record = BaselineContext(
            participant_id=participant.id,
            contract_version=payload.contract_version,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            support_confidence=support,
            support_confidence_nonresponse=support_nr,
            everyday_comfort=everyday,
            everyday_comfort_nonresponse=everyday_nr,
            insecurity_comfort=insecurity,
            insecurity_comfort_nonresponse=insecurity_nr,
            completed_at=clock(),
        )
        session.add(record)
        audit(session, participant.id, "submission_accepted", "baseline_context", "created")
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            audit(session, participant.id, "submission_rejected", "baseline_context", "duplicate")
            session.commit()
            raise ApiError(
                409, "duplicate_submission", "Baseline context was already submitted."
            ) from error
        return SubmissionResponse(id=record.id, status="created")

    @application.post("/v1/assessments", response_model=SubmissionResponse, status_code=201)
    def submit_assessment(
        raw_payload: dict[str, Any],
        participant: Participant = Depends(current_participant),
        session: Session = Depends(get_session),
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=64),
    ) -> SubmissionResponse | JSONResponse:
        try:
            payload = AssessmentPayload.model_validate(raw_payload)
        except ValidationError as error:
            audit(session, participant.id, "submission_rejected", "assessments", "contract")
            session.commit()
            raise ApiError(
                422, "invalid_contract", "The assessment contract is invalid."
            ) from error
        payload_hash = canonical_hash(payload.model_dump(by_alias=True, mode="json"))
        replay = session.scalar(
            select(Assessment).where(
                Assessment.participant_id == participant.id,
                Assessment.idempotency_key == idempotency_key,
            )
        )
        if replay is not None:
            if replay.payload_hash != payload_hash:
                audit(session, participant.id, "submission_rejected", "assessments", "conflict")
                session.commit()
                raise ApiError(
                    409, "idempotency_conflict", "This retry conflicts with the original."
                )
            return JSONResponse(
                status_code=200,
                content=SubmissionResponse(id=replay.id, status="replayed").model_dump(),
            )

        existing = session.scalar(
            select(Assessment).where(
                Assessment.participant_id == participant.id,
                Assessment.assessment_type == payload.assessment_type,
            )
        )
        if existing is not None:
            audit(session, participant.id, "submission_rejected", "assessments", "duplicate")
            session.commit()
            raise ApiError(409, "duplicate_submission", "That assessment was already submitted.")
        if (
            payload.assessment_type == "follow_up"
            and session.scalar(
                select(Assessment.id).where(
                    Assessment.participant_id == participant.id,
                    Assessment.assessment_type == "baseline",
                )
            )
            is None
        ):
            audit(session, participant.id, "submission_rejected", "assessments", "state")
            session.commit()
            raise ApiError(409, "invalid_state", "A baseline assessment is required first.")
        try:
            assert_submission_window(
                participant,
                clock(),
                assessment_type=payload.assessment_type,
                enforce=active_settings.enforce_study_windows,
            )
        except ApiError:
            audit(session, participant.id, "submission_rejected", "assessments", "window")
            session.commit()
            raise

        record = Assessment(
            participant_id=participant.id,
            assessment_type=payload.assessment_type,
            instrument_name=payload.instrument_name,
            instrument_version=payload.instrument_version,
            language=payload.language,
            contract_version=payload.contract_version,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            item_responses=[item.model_dump(by_alias=True) for item in payload.responses],
            total_score=score_assessment(payload),
            completed_at=clock(),
        )
        session.add(record)
        audit(session, participant.id, "submission_accepted", "assessments", "created")
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            audit(session, participant.id, "submission_rejected", "assessments", "duplicate")
            session.commit()
            raise ApiError(
                409, "duplicate_submission", "That assessment was already submitted."
            ) from error
        return SubmissionResponse(id=record.id, status="created")

    @application.post("/v1/check-ins", response_model=SubmissionResponse, status_code=201)
    def submit_check_in(
        raw_payload: dict[str, Any],
        participant: Participant = Depends(current_participant),
        session: Session = Depends(get_session),
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=64),
    ) -> SubmissionResponse | JSONResponse:
        try:
            payload = validate_check_in(raw_payload)
        except (ValidationError, UnsupportedContractVersionError) as error:
            audit(session, participant.id, "submission_rejected", "check_ins", "contract")
            session.commit()
            raise ApiError(422, "invalid_contract", "The check-in contract is invalid.") from error
        payload_hash = canonical_hash(payload.model_dump(by_alias=True, mode="json"))
        replay = session.scalar(
            select(CheckIn).where(
                CheckIn.participant_id == participant.id,
                CheckIn.idempotency_key == idempotency_key,
            )
        )
        if replay is not None:
            if replay.payload_hash != payload_hash:
                audit(session, participant.id, "submission_rejected", "check_ins", "conflict")
                session.commit()
                raise ApiError(
                    409, "idempotency_conflict", "This retry conflicts with the original."
                )
            return JSONResponse(
                status_code=200,
                content=SubmissionResponse(id=replay.id, status="replayed").model_dump(),
            )
        if session.scalar(
            select(CheckIn).where(
                CheckIn.participant_id == participant.id, CheckIn.week == payload.week
            )
        ):
            audit(session, participant.id, "submission_rejected", "check_ins", "duplicate")
            session.commit()
            raise ApiError(409, "duplicate_submission", "That weekly check-in already exists.")
        try:
            assert_submission_window(
                participant,
                clock(),
                week=payload.week,
                enforce=active_settings.enforce_study_windows,
            )
        except ApiError:
            audit(session, participant.id, "submission_rejected", "check_ins", "window")
            session.commit()
            raise

        expected = payload.expected_comfort if isinstance(payload.expected_comfort, int) else None
        expected_nr = (
            payload.expected_comfort if isinstance(payload.expected_comfort, str) else None
        )
        support = (
            payload.support_confidence if isinstance(payload.support_confidence, int) else None
        )
        support_nr = (
            payload.support_confidence if isinstance(payload.support_confidence, str) else None
        )
        record = CheckIn(
            participant_id=participant.id,
            week=payload.week,
            contract_version=payload.contract_version,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            wanted_to_share=payload.wanted_to_share,
            intended_audience=payload.intended_audience,
            sharing_action=payload.sharing_action,
            expected_comfort=expected,
            expected_comfort_nonresponse=expected_nr,
            anticipated_judgment=payload.anticipated_judgment,
            support_confidence=support,
            support_confidence_nonresponse=support_nr,
            concern_category=payload.concern_category,
            completed_at=clock(),
        )
        session.add(record)
        audit(session, participant.id, "submission_accepted", "check_ins", "created")
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            audit(session, participant.id, "submission_rejected", "check_ins", "duplicate")
            session.commit()
            raise ApiError(
                409, "duplicate_submission", "That weekly check-in already exists."
            ) from error
        return SubmissionResponse(id=record.id, status="created")

    @application.get("/v1/me/trends", response_model=TrendsResponse)
    def trends(
        participant: Participant = Depends(current_participant),
        session: Session = Depends(get_session),
    ) -> TrendsResponse:
        rows = session.scalars(
            select(CheckIn).where(CheckIn.participant_id == participant.id).order_by(CheckIn.week)
        ).all()
        eligible = [row for row in rows if row.wanted_to_share == "yes"]
        shared = sum(row.sharing_action == "shared" for row in eligible)
        kept_private = sum(row.sharing_action == "chose_private" for row in eligible)
        if not eligible:
            message = "There is not enough information to summarize this pattern."
        else:
            message = (
                f"In {shared} of {len(eligible)} check-ins where you wanted to talk with "
                "someone, you reported talking with them."
            )
        return TrendsResponse(
            contractVersion="1.0.0-draft",
            completedCheckIns=len(rows),
            eligibleWantedWeeks=len(eligible),
            sharedWeeks=shared,
            keptPrivateWeeks=kept_private,
            summaryAvailable=bool(eligible),
            message=message,
        )

    @application.delete("/v1/me", response_model=DeletionResponse)
    def delete_me(
        participant: Participant = Depends(current_participant),
        session: Session = Depends(get_session),
    ) -> DeletionResponse:
        now = clock()
        audit(session, participant.id, "withdrawal_requested", "me", "accepted")
        session.add(
            ConsentEvent(
                participant_id=participant.id,
                consent_version=active_settings.consent_version,
                action="withdraw",
                occurred_at=now,
            )
        )
        session.execute(delete(Assessment).where(Assessment.participant_id == participant.id))
        session.execute(delete(CheckIn).where(CheckIn.participant_id == participant.id))
        session.execute(
            delete(BaselineContext).where(BaselineContext.participant_id == participant.id)
        )
        participant.withdrawal_state = "deleted"
        participant.deleted_at = now
        participant.session_token_hash = None
        participant.recovery_code_hash = None
        audit(session, participant.id, "deletion_completed", "me", "tombstoned")
        session.commit()
        return DeletionResponse(
            status="deleted",
            message="Your submitted responses and access credentials were deleted.",
        )

    return application


app = create_app()
