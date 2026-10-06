from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator


class WireModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class EnrollmentRequest(WireModel):
    contract_version: Literal["1.0.0-draft"] = Field(alias="contractVersion")
    age_band: Literal["under_18", "18_19", "20_22", "23_or_older", "prefer_not_to_answer"] = Field(
        alias="ageBand"
    )
    consent_version: str = Field(alias="consentVersion", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    consent_action: Literal["agree", "do_not_agree"] = Field(alias="consentAction")


class EnrollmentResponse(WireModel):
    participant_id: str = Field(alias="participantId")
    session_token: str = Field(alias="sessionToken")
    recovery_code: str = Field(alias="recoveryCode")
    contract_version: str = Field(alias="contractVersion")


class RecoveryRequest(WireModel):
    participant_id: str = Field(alias="participantId")
    recovery_code: str = Field(alias="recoveryCode", min_length=8, max_length=80)


class SessionResponse(WireModel):
    session_token: str = Field(alias="sessionToken")


class BaselineContextSubmission(WireModel):
    contract_version: Literal["1.0.0-draft"] = Field(alias="contractVersion")
    support_confidence: StrictInt | Literal["no_person", "prefer_not_to_answer"] = Field(
        alias="supportConfidence"
    )
    everyday_comfort: StrictInt | Literal["not_applicable", "prefer_not_to_answer"] = Field(
        alias="everydayComfort"
    )
    insecurity_comfort: StrictInt | Literal["not_applicable", "prefer_not_to_answer"] = Field(
        alias="insecurityComfort"
    )
    completed_at: datetime = Field(alias="completedAt")

    @model_validator(mode="after")
    def ordinals_are_in_range(self) -> BaselineContextSubmission:
        values = (self.support_confidence, self.everyday_comfort, self.insecurity_comfort)
        if any(isinstance(value, int) and not 1 <= value <= 5 for value in values):
            raise ValueError("numeric ordinal responses must be between 1 and 5")
        return self


class AssessmentItem(WireModel):
    item_code: str = Field(alias="itemCode", pattern=r"^SAD(0[1-9]|10)$")
    response_code: StrictInt | Literal["prefer_not_to_answer"] = Field(alias="responseCode")

    @model_validator(mode="after")
    def response_is_in_range(self) -> AssessmentItem:
        if isinstance(self.response_code, int) and not 0 <= self.response_code <= 4:
            raise ValueError("numeric responseCode must be between 0 and 4")
        return self


class AssessmentSubmission(WireModel):
    contract_version: Literal["1.0.0-draft"] = Field(alias="contractVersion")
    assessment_type: Literal["baseline", "follow_up"] = Field(alias="assessmentType")
    instrument_name: Literal["apa_dsm5tr_sad_adult"] = Field(alias="instrumentName")
    instrument_version: Literal["DSM-5-TR-2022"] = Field(alias="instrumentVersion")
    language: Literal["en"]
    responses: list[AssessmentItem] = Field(min_length=10, max_length=10)
    completed_at: datetime = Field(alias="completedAt")

    @model_validator(mode="after")
    def items_are_complete_and_ordered(self) -> AssessmentSubmission:
        expected = [f"SAD{item:02d}" for item in range(1, 11)]
        actual = [item.item_code for item in self.responses]
        if actual != expected:
            raise ValueError("responses must contain SAD01 through SAD10 in order")
        return self


class SubmissionResponse(WireModel):
    id: str
    status: Literal["created", "replayed"]


class TrendsResponse(WireModel):
    contract_version: Literal["1.0.0-draft"] = Field(alias="contractVersion")
    completed_check_ins: int = Field(alias="completedCheckIns", ge=0, le=4)
    eligible_wanted_weeks: int = Field(alias="eligibleWantedWeeks", ge=0, le=4)
    shared_weeks: int = Field(alias="sharedWeeks", ge=0, le=4)
    kept_private_weeks: int = Field(alias="keptPrivateWeeks", ge=0, le=4)
    summary_available: bool = Field(alias="summaryAvailable")
    message: str


class DeletionResponse(WireModel):
    status: Literal["deleted"]
    message: str
