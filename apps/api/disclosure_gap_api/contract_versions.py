from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

ROOT = Path(__file__).parents[3]

type WantedToShare = Literal["yes", "no", "not_sure", "prefer_not_to_answer"]
type IntendedAudience = Literal[
    "friend",
    "family",
    "partner",
    "other_trusted",
    "no_particular_person",
    "prefer_not_to_answer",
]
type SharingAction = Literal[
    "shared",
    "not_shared",
    "chose_private",
    "no_safe_opportunity",
    "not_applicable",
    "prefer_not_to_answer",
]
type OrdinalResponse = StrictInt | Literal["not_applicable", "prefer_not_to_answer"]
type AnticipatedJudgment = Literal[
    "yes", "no", "shared_as_wanted", "not_applicable", "prefer_not_to_answer"
]
type ConcernCategory = Literal["everyday", "personal_insecurity", "other", "prefer_not_to_answer"]


class UnsupportedContractVersionError(ValueError):
    """Raised before parsing when no deliberate mapping exists for a version."""


class CheckInBase(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    week: int = Field(strict=True, ge=1, le=4)
    wanted_to_share: WantedToShare = Field(alias="wantedToShare")
    intended_audience: IntendedAudience | None = Field(default=None, alias="intendedAudience")
    sharing_action: SharingAction | None = Field(default=None, alias="sharingAction")
    expected_comfort: OrdinalResponse | None = Field(default=None, alias="expectedComfort")
    anticipated_judgment: AnticipatedJudgment | None = Field(
        default=None, alias="anticipatedJudgment"
    )
    support_confidence: OrdinalResponse | None = Field(default=None, alias="supportConfidence")
    concern_category: ConcernCategory | None = Field(default=None, alias="concernCategory")
    completed_at: datetime = Field(alias="completedAt")

    @model_validator(mode="after")
    def enforce_skip_logic(self) -> CheckInBase:
        followups = (
            self.intended_audience,
            self.sharing_action,
            self.expected_comfort,
            self.anticipated_judgment,
            self.support_confidence,
            self.concern_category,
        )
        if self.wanted_to_share == "yes" and any(value is None for value in followups):
            raise ValueError("all follow-up fields are required when wantedToShare is yes")
        if self.wanted_to_share != "yes" and any(value is not None for value in followups):
            raise ValueError("follow-up fields are forbidden when wantedToShare is not yes")
        numeric_ordinals = (self.expected_comfort, self.support_confidence)
        if any(isinstance(value, int) and not 1 <= value <= 5 for value in numeric_ordinals):
            raise ValueError("numeric ordinal responses must be between 1 and 5")
        return self


class CheckInV100(CheckInBase):
    contract_version: Literal["1.0.0-draft"] = Field(alias="contractVersion")


class CheckInV110Fixture(CheckInBase):
    contract_version: Literal["1.1.0-fixture"] = Field(alias="contractVersion")
    client_submission_id: UUID | None = Field(default=None, alias="clientSubmissionId")


type SupportedCheckIn = CheckInV100 | CheckInV110Fixture

SCHEMA_PATHS = {
    "1.0.0-draft": ROOT / "packages/contracts/v1/check-in.schema.json",
    "1.1.0-fixture": ROOT / "packages/contracts/fixtures/v1_1/check-in.schema.json",
}


def validate_check_in(payload: dict[str, Any]) -> SupportedCheckIn:
    """Validate at the API boundary by dispatching an exact contract version."""
    version = payload.get("contractVersion")
    if version == "1.0.0-draft":
        return CheckInV100.model_validate(payload)
    if version == "1.1.0-fixture":
        return CheckInV110Fixture.model_validate(payload)
    raise UnsupportedContractVersionError(f"unsupported check-in contract version: {version!r}")


def schema_fingerprint(contract_version: str) -> str:
    """Return the fingerprint of the exact schema used to interpret a record."""
    try:
        schema_path = SCHEMA_PATHS[contract_version]
    except KeyError as error:
        raise UnsupportedContractVersionError(
            f"unsupported check-in contract version: {contract_version!r}"
        ) from error
    return hashlib.sha256(schema_path.read_bytes()).hexdigest()


def to_feature_input(record: SupportedCheckIn) -> dict[str, object]:
    """Project stable feature inputs without erasing their source contract."""
    shared: bool | None = None
    if record.sharing_action == "shared":
        shared = True
    elif record.sharing_action in {"not_shared", "chose_private"}:
        shared = False

    return {
        "source_contract_version": record.contract_version,
        "week": record.week,
        "wanted_to_share_response": record.wanted_to_share,
        "eligible_wanted_to_share": record.wanted_to_share == "yes",
        "sharing_action": record.sharing_action,
        "shared": shared,
        "completed_at": record.completed_at.isoformat(),
    }


def to_export_envelope(record: SupportedCheckIn) -> dict[str, object]:
    """Wrap a validated payload with immutable interpretation metadata."""
    return {
        "record_type": "check_in",
        "contract_version": record.contract_version,
        "schema_fingerprint": schema_fingerprint(record.contract_version),
        "payload": record.model_dump(by_alias=True, mode="json", exclude_none=True),
    }
