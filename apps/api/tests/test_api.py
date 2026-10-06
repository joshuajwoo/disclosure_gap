from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from apps.api.disclosure_gap_api.config import Settings
from apps.api.disclosure_gap_api.main import create_app
from apps.api.disclosure_gap_api.models import (
    Assessment,
    Base,
    BaselineContext,
    CheckIn,
    Participant,
    StudyEvent,
)
from research.etl import load_export
from research.export import create_restricted_export
from research.features import build_features


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 1, 5, 9, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, *, days: int) -> None:
        self.value += timedelta(days=days)


@pytest.fixture
def api() -> tuple[TestClient, Any, Clock]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    clock = Clock()
    app = create_app(
        settings=Settings(app_env="test", database_url="sqlite://", enforce_study_windows=True),
        engine=engine,
        clock=clock,
    )
    with TestClient(app) as client:
        yield client, engine, clock


def enroll(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/v1/participants",
        json={
            "contractVersion": "1.0.0-draft",
            "ageBand": "18_19",
            "consentVersion": "0.2.0",
            "consentAction": "agree",
        },
    )
    assert response.status_code == 201
    return response.json()


def headers(token: str, key: str = "retry-key-0001") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Idempotency-Key": key}


def assessment_payload(kind: str = "baseline", score: int = 2) -> dict[str, Any]:
    return {
        "contractVersion": "1.0.0-draft",
        "assessmentType": kind,
        "instrumentName": "apa_dsm5tr_sad_adult",
        "instrumentVersion": "DSM-5-TR-2022",
        "language": "en",
        "responses": [
            {"itemCode": f"SAD{item:02d}", "responseCode": score} for item in range(1, 11)
        ],
        "completedAt": "1999-01-01T00:00:00Z",
    }


def wanted_check_in(week: int = 1, action: str = "chose_private") -> dict[str, Any]:
    return {
        "contractVersion": "1.0.0-draft",
        "week": week,
        "wantedToShare": "yes",
        "intendedAudience": "friend",
        "sharingAction": action,
        "expectedComfort": 2,
        "anticipatedJudgment": "yes",
        "supportConfidence": 3,
        "concernCategory": "personal_insecurity",
        "completedAt": "1999-01-01T00:00:00Z",
    }


def baseline_context_payload() -> dict[str, Any]:
    return {
        "contractVersion": "1.0.0-draft",
        "supportConfidence": "no_person",
        "everydayComfort": 4,
        "insecurityComfort": "prefer_not_to_answer",
        "completedAt": "1999-01-01T00:00:00Z",
    }


def test_baseline_context_preserves_nonresponse_and_is_idempotent(
    api: tuple[TestClient, Any, Clock],
) -> None:
    client, engine, _clock = api
    credentials = enroll(client)
    auth = headers(credentials["sessionToken"], "baseline-context-key")
    created = client.post("/v1/baseline-context", headers=auth, json=baseline_context_payload())
    assert created.status_code == 201
    replay = client.post("/v1/baseline-context", headers=auth, json=baseline_context_payload())
    assert replay.status_code == 200
    changed = baseline_context_payload() | {"everydayComfort": 2}
    conflict = client.post("/v1/baseline-context", headers=auth, json=changed)
    assert conflict.status_code == 409
    with Session(engine) as session:
        context = session.scalar(select(BaselineContext))
        assert context is not None
        assert context.support_confidence is None
        assert context.support_confidence_nonresponse == "no_person"
        assert context.everyday_comfort == 4
        assert context.insecurity_comfort_nonresponse == "prefer_not_to_answer"


def test_enrollment_recovery_and_generic_failures(api: tuple[TestClient, Any, Clock]) -> None:
    client, engine, _clock = api
    credentials = enroll(client)
    with Session(engine) as session:
        participant = session.get(Participant, credentials["participantId"])
        assert participant is not None
        assert participant.session_token_hash != credentials["sessionToken"]
        assert participant.recovery_code_hash != credentials["recoveryCode"]
        assert participant.recovery_code_hash.startswith("scrypt$")

    recovered = client.post(
        "/v1/sessions/recover",
        json={
            "participantId": credentials["participantId"],
            "recoveryCode": credentials["recoveryCode"],
        },
    )
    assert recovered.status_code == 200
    assert recovered.json()["sessionToken"] != credentials["sessionToken"]
    assert (
        client.get("/v1/me/trends", headers=headers(credentials["sessionToken"])).status_code == 401
    )
    failure = client.post(
        "/v1/sessions/recover",
        json={"participantId": credentials["participantId"], "recoveryCode": "WRONG-CODE"},
    )
    assert failure.status_code == 401
    assert "participant" not in failure.json()["error"]["message"].lower()


def test_participant_isolation_and_neutral_trends(api: tuple[TestClient, Any, Clock]) -> None:
    client, _engine, _clock = api
    first = enroll(client)
    second = enroll(client)
    created = client.post(
        "/v1/check-ins",
        headers=headers(first["sessionToken"], "check-in-first"),
        json=wanted_check_in(action="shared"),
    )
    assert created.status_code == 201
    first_trends = client.get(
        "/v1/me/trends", headers={"Authorization": f"Bearer {first['sessionToken']}"}
    ).json()
    second_trends = client.get(
        "/v1/me/trends", headers={"Authorization": f"Bearer {second['sessionToken']}"}
    ).json()
    assert first_trends["completedCheckIns"] == 1
    assert first_trends["sharedWeeks"] == 1
    assert "diagnos" not in first_trends["message"].lower()
    assert second_trends["completedCheckIns"] == 0
    assert second_trends["summaryAvailable"] is False


def test_assessment_idempotency_conflict_order_and_windows(
    api: tuple[TestClient, Any, Clock],
) -> None:
    client, engine, clock = api
    credentials = enroll(client)
    auth = headers(credentials["sessionToken"], "baseline-key")
    created = client.post("/v1/assessments", headers=auth, json=assessment_payload())
    assert created.status_code == 201
    replayed = client.post("/v1/assessments", headers=auth, json=assessment_payload())
    assert replayed.status_code == 200
    assert replayed.json()["id"] == created.json()["id"]
    changed = assessment_payload(score=3)
    conflict = client.post("/v1/assessments", headers=auth, json=changed)
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"

    follow_up_early = client.post(
        "/v1/assessments",
        headers=headers(credentials["sessionToken"], "follow-up-key"),
        json=assessment_payload("follow_up"),
    )
    assert follow_up_early.status_code == 409
    assert follow_up_early.json()["error"]["code"] == "window_closed"
    clock.advance(days=29)
    follow_up = client.post(
        "/v1/assessments",
        headers=headers(credentials["sessionToken"], "follow-up-key-2"),
        json=assessment_payload("follow_up"),
    )
    assert follow_up.status_code == 201
    with Session(engine) as session:
        scores = session.scalars(
            select(Assessment.total_score).order_by(Assessment.assessment_type)
        ).all()
        assert scores == [20, 20]


def test_follow_up_requires_baseline_even_when_window_is_open(
    api: tuple[TestClient, Any, Clock],
) -> None:
    client, _engine, clock = api
    credentials = enroll(client)
    clock.advance(days=29)
    response = client.post(
        "/v1/assessments",
        headers=headers(credentials["sessionToken"], "follow-up-no-baseline"),
        json=assessment_payload("follow_up"),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "invalid_state"


def test_check_in_versions_duplicates_invalid_contract_and_window(
    api: tuple[TestClient, Any, Clock],
) -> None:
    client, engine, clock = api
    credentials = enroll(client)
    token = credentials["sessionToken"]
    payload = wanted_check_in()
    first = client.post("/v1/check-ins", headers=headers(token, "week-one-key"), json=payload)
    assert first.status_code == 201
    assert (
        client.post(
            "/v1/check-ins", headers=headers(token, "week-one-key"), json=payload
        ).status_code
        == 200
    )
    duplicate = client.post("/v1/check-ins", headers=headers(token, "week-one-other"), json=payload)
    assert duplicate.status_code == 409

    unsupported = payload | {"contractVersion": "2.0.0-unsupported"}
    rejected = client.post(
        "/v1/check-ins", headers=headers(token, "unsupported-key"), json=unsupported
    )
    assert rejected.status_code == 422
    assert rejected.json()["error"]["code"] == "invalid_contract"

    clock.advance(days=7)
    fixture_payload = wanted_check_in(week=2) | {
        "contractVersion": "1.1.0-fixture",
        "clientSubmissionId": "f6ad3167-fce0-4bf3-89e7-2e46b377c9fb",
    }
    fixture = client.post(
        "/v1/check-ins", headers=headers(token, "week-two-key"), json=fixture_payload
    )
    assert fixture.status_code == 201
    late = client.post(
        "/v1/check-ins",
        headers=headers(token, "late-week-one"),
        json=wanted_check_in(week=1),
    )
    assert late.status_code == 409
    assert late.json()["error"]["code"] == "duplicate_submission"
    wrong_week = client.post(
        "/v1/check-ins",
        headers=headers(token, "wrong-window-week"),
        json=wanted_check_in(week=3),
    )
    assert wrong_week.status_code == 409
    assert wrong_week.json()["error"]["code"] == "window_closed"
    with Session(engine) as session:
        assert session.scalars(select(CheckIn.contract_version).order_by(CheckIn.week)).all() == [
            "1.0.0-draft",
            "1.1.0-fixture",
        ]


def test_deletion_revokes_access_and_removes_responses(api: tuple[TestClient, Any, Clock]) -> None:
    client, engine, _clock = api
    credentials = enroll(client)
    token = credentials["sessionToken"]
    client.post(
        "/v1/check-ins",
        headers=headers(token, "delete-check-in"),
        json=wanted_check_in(),
    )
    client.post(
        "/v1/baseline-context",
        headers=headers(token, "delete-baseline-context"),
        json=baseline_context_payload(),
    )
    deleted = client.delete("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert deleted.status_code == 200
    assert (
        client.get("/v1/me/trends", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    )
    recovery = client.post(
        "/v1/sessions/recover",
        json={
            "participantId": credentials["participantId"],
            "recoveryCode": credentials["recoveryCode"],
        },
    )
    assert recovery.status_code == 401
    with Session(engine) as session:
        participant = session.get(Participant, credentials["participantId"])
        assert participant is not None
        assert participant.withdrawal_state == "deleted"
        assert participant.session_token_hash is None
        assert session.scalar(select(func.count()).select_from(CheckIn)) == 0
        assert session.scalar(select(func.count()).select_from(BaselineContext)) == 0
        event_types = set(session.scalars(select(StudyEvent.event_type)))
        assert {"withdrawal_requested", "deletion_completed"} <= event_types


def test_logs_and_errors_do_not_echo_credentials_or_payloads(
    api: tuple[TestClient, Any, Clock], caplog: pytest.LogCaptureFixture
) -> None:
    client, _engine, _clock = api
    credentials = enroll(client)
    caplog.set_level(logging.INFO, logger="disclosure_gap_api")
    secret_token = credentials["sessionToken"]
    response = client.post(
        "/v1/check-ins",
        headers=headers(secret_token, "redaction-key"),
        json={"contractVersion": "2.0.0-unsupported", "privateValue": "DO-NOT-LOG-ME"},
    )
    assert response.status_code == 422
    rendered = caplog.text
    assert secret_token not in rendered
    assert credentials["recoveryCode"] not in rendered
    assert "DO-NOT-LOG-ME" not in rendered
    assert "privateValue" not in response.text


def test_contract_validation_rejects_boolean_and_out_of_range_scores(
    api: tuple[TestClient, Any, Clock],
) -> None:
    client, _engine, _clock = api
    credentials = enroll(client)
    assessment = assessment_payload()
    assessment["responses"][0]["responseCode"] = True
    response = client.post(
        "/v1/assessments",
        headers=headers(credentials["sessionToken"], "invalid-score-key"),
        json=assessment,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_contract"

    check_in = wanted_check_in()
    check_in["expectedComfort"] = 6
    response = client.post(
        "/v1/check-ins",
        headers=headers(credentials["sessionToken"], "invalid-ordinal"),
        json=check_in,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_contract"


def test_complete_api_export_feature_and_deletion_vertical_slice(
    api: tuple[TestClient, Any, Clock], tmp_path: Path
) -> None:
    client, engine, clock = api
    credentials = enroll(client)
    token = credentials["sessionToken"]
    assert (
        client.post(
            "/v1/baseline-context",
            headers=headers(token, "vertical-context"),
            json=baseline_context_payload(),
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/v1/assessments",
            headers=headers(token, "vertical-baseline"),
            json=assessment_payload("baseline", 1),
        ).status_code
        == 201
    )
    for week, action in enumerate(["chose_private", "shared", "not_shared", "shared"], start=1):
        if week > 1:
            clock.advance(days=7)
        assert (
            client.post(
                "/v1/check-ins",
                headers=headers(token, f"vertical-week-{week}"),
                json=wanted_check_in(week, action),
            ).status_code
            == 201
        )
    clock.advance(days=8)
    assert (
        client.post(
            "/v1/assessments",
            headers=headers(token, "vertical-follow-up"),
            json=assessment_payload("follow_up", 2),
        ).status_code
        == 201
    )
    trends = client.get("/v1/me/trends", headers={"Authorization": f"Bearer {token}"}).json()
    assert trends["completedCheckIns"] == 4
    assert trends["sharedWeeks"] == 2
    with Session(engine) as session:
        create_restricted_export(
            session,
            tmp_path / "restricted-export",
            authorized_role="research_exporter",
            approval_id="SYNTHETIC-INTEGRATION-ONLY",
        )
    features = build_features(load_export(tmp_path / "restricted-export"))
    assert features["intention_action_gap"][0] == pytest.approx(0.5)
    assert features["baseline_score"][0] == 10
    assert features["follow_up_score"][0] == 20
    assert client.delete("/v1/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(CheckIn)) == 0
