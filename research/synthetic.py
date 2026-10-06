from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from apps.api.disclosure_gap_api.contract_versions import validate_check_in
from apps.api.disclosure_gap_api.schemas import AssessmentSubmission

GENERATOR_VERSION = "1.0.0"
SCENARIOS: dict[str, dict[str, float | str]] = {
    "null": {
        "directGapEffect": 0.0,
        "confounderEffect": 0.0,
        "expectedAdjustedDirection": "zero",
    },
    "weak_effect": {
        "directGapEffect": 2.0,
        "confounderEffect": 0.0,
        "expectedAdjustedDirection": "positive-small",
    },
    "known_effect": {
        "directGapEffect": 8.0,
        "confounderEffect": 0.0,
        "expectedAdjustedDirection": "positive",
    },
    "confounded": {
        "directGapEffect": 0.0,
        "confounderEffect": 6.0,
        "expectedAdjustedDirection": "positive-confounded",
    },
    "missingness": {
        "directGapEffect": 4.0,
        "confounderEffect": 0.0,
        "expectedAdjustedDirection": "positive-with-missingness",
    },
    "attrition": {
        "directGapEffect": 4.0,
        "confounderEffect": 0.0,
        "expectedAdjustedDirection": "positive-with-attrition",
    },
}


def stable_id(seed: int, scenario: str, index: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"disclosure-gap:{seed}:{scenario}:{index}"))


def score_responses(score: int) -> list[dict[str, int | str]]:
    remaining = max(0, min(40, score))
    values: list[int] = []
    for slots_left in range(10, 0, -1):
        value = min(4, remaining // slots_left)
        values.append(value)
        remaining -= value
    index = 9
    while remaining:
        if values[index] < 4:
            values[index] += 1
            remaining -= 1
        index = (index - 1) % 10
    return [
        {"itemCode": f"SAD{item:02d}", "responseCode": value}
        for item, value in enumerate(values, start=1)
    ]


def assessment(kind: str, score: int, completed_at: datetime) -> dict[str, Any]:
    return {
        "contractVersion": "1.0.0-draft",
        "assessmentType": kind,
        "instrumentName": "apa_dsm5tr_sad_adult",
        "instrumentVersion": "DSM-5-TR-2022",
        "language": "en",
        "responses": score_responses(score),
        "completedAt": completed_at.isoformat().replace("+00:00", "Z"),
    }


def make_check_in(
    *,
    version: str,
    week: int,
    nonsharing_weeks: int,
    start: datetime,
    index: int,
    prefer_not_to_answer: bool = False,
    no_desire: bool = False,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "contractVersion": version,
        "week": week,
        "wantedToShare": "prefer_not_to_answer"
        if prefer_not_to_answer
        else "no"
        if no_desire
        else "yes",
        "completedAt": (start + timedelta(days=7 * (week - 1), hours=12))
        .isoformat()
        .replace("+00:00", "Z"),
    }
    if version == "1.1.0-fixture":
        record["clientSubmissionId"] = str(
            uuid.uuid5(uuid.NAMESPACE_URL, f"submission:{index}:{week}")
        )
    if record["wantedToShare"] == "yes":
        record.update(
            {
                "intendedAudience": "friend" if week % 2 else "family",
                "sharingAction": "chose_private" if week <= nonsharing_weeks else "shared",
                "expectedComfort": 1 + ((index + week) % 5),
                "anticipatedJudgment": "yes" if week <= nonsharing_weeks else "shared_as_wanted",
                "supportConfidence": 1 + ((index + week + 1) % 5),
                "concernCategory": "personal_insecurity" if week % 2 else "everyday",
            }
        )
    return record


def intention_action_gap(check_ins: list[dict[str, Any]]) -> float | None:
    if len(check_ins) < 3:
        return None
    eligible = [
        row
        for row in check_ins
        if row.get("wantedToShare") == "yes"
        and row.get("sharingAction") in {"shared", "not_shared", "chose_private"}
    ]
    if not eligible:
        return None
    held = sum(row["sharingAction"] in {"not_shared", "chose_private"} for row in eligible)
    return held / len(eligible)


def generate_scenario(name: str, *, seed: int, size: int = 20) -> dict[str, Any]:
    if name not in SCENARIOS:
        raise ValueError(f"unknown synthetic scenario: {name}")
    if size < 8:
        raise ValueError("scenario size must be at least 8")
    parameters = SCENARIOS[name]
    rng = random.Random(f"{seed}:{name}")
    start = datetime(2026, 1, 5, 9, tzinfo=UTC)
    participants: list[dict[str, Any]] = []

    for index in range(size):
        participant_id = stable_id(seed, name, index)
        version = "1.0.0-draft" if index % 2 == 0 else "1.1.0-fixture"
        nonsharing_weeks = index % 5
        check_ins = [
            make_check_in(
                version=version,
                week=week,
                nonsharing_weeks=nonsharing_weeks,
                start=start,
                index=index,
                prefer_not_to_answer=index == 3 and week == 4,
                no_desire=index == 4,
            )
            for week in range(1, 5)
        ]
        if name == "missingness" and index % 4 == 0:
            check_ins = check_ins[:2]

        gap = intention_action_gap(check_ins)
        baseline_score = 16 + ((index * 7) % 9)
        centered_gap = (gap if gap is not None else 0.5) - 0.5
        confounder = centered_gap if name == "confounded" else 0.0
        jitter = rng.choice([-1, 0, 1]) if name not in {"null", "weak_effect"} else 0
        follow_up_score = round(
            baseline_score
            + float(parameters["directGapEffect"]) * centered_gap
            + float(parameters["confounderEffect"]) * confounder
            + jitter
        )
        follow_up_score = max(0, min(40, follow_up_score))
        withdrawn = name == "attrition" and index % 5 == 0
        assessments = [assessment("baseline", baseline_score, start - timedelta(hours=1))]
        if not withdrawn:
            assessments.append(assessment("follow_up", follow_up_score, start + timedelta(days=29)))

        participants.append(
            {
                "participantId": participant_id,
                "synthetic": True,
                "scenario": name,
                "contractVersion": version,
                "ageBand": "18_19" if index % 2 == 0 else "20_22",
                "withdrawalState": "deleted" if withdrawn else "active",
                "baselineContext": {
                    "contractVersion": "1.0.0-draft",
                    "supportConfidence": 1 + ((index + 1) % 5),
                    "everydayComfort": 1 + ((index + 2) % 5),
                    "insecurityComfort": 1 + (index % 5),
                    "completedAt": (start - timedelta(minutes=30))
                    .isoformat()
                    .replace("+00:00", "Z"),
                },
                "assessments": assessments,
                "checkIns": check_ins,
                "expectedFeatures": {
                    "completedCheckIns": len(check_ins),
                    "intentionActionGap": gap,
                    "exclusionReason": (
                        "fewer_than_3_check_ins"
                        if len(check_ins) < 3
                        else "no_eligible_wanted_weeks"
                        if gap is None
                        else None
                    ),
                },
            }
        )

    return {
        "metadata": {
            "synthetic": True,
            "generatorVersion": GENERATOR_VERSION,
            "seed": seed,
            "scenario": name,
            "parameters": parameters,
        },
        "participants": participants,
    }


def generate_all(*, seed: int = 20261004, size: int = 20) -> dict[str, Any]:
    return {
        "metadata": {
            "synthetic": True,
            "generatorVersion": GENERATOR_VERSION,
            "seed": seed,
            "purpose": "pipeline-validation-only-not-empirical-evidence",
        },
        "cohorts": [generate_scenario(name, seed=seed, size=size) for name in SCENARIOS],
    }


def _slope(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 2:
        return None
    mean_x = sum(pair[0] for pair in pairs) / len(pairs)
    mean_y = sum(pair[1] for pair in pairs) / len(pairs)
    denominator = sum((pair[0] - mean_x) ** 2 for pair in pairs)
    if denominator == 0:
        return None
    return sum((x - mean_x) * (y - mean_y) for x, y in pairs) / denominator


def validate_dataset(dataset: dict[str, Any]) -> dict[str, dict[str, float | int | None]]:
    if dataset.get("metadata", {}).get("synthetic") is not True:
        raise ValueError("dataset is not marked synthetic")
    summaries: dict[str, dict[str, float | int | None]] = {}
    seen_ids: set[str] = set()
    for cohort in dataset.get("cohorts", []):
        metadata = cohort["metadata"]
        if metadata.get("synthetic") is not True:
            raise ValueError("cohort is not marked synthetic")
        pairs: list[tuple[float, float]] = []
        missing_features = 0
        attrited = 0
        for participant in cohort["participants"]:
            if participant.get("synthetic") is not True:
                raise ValueError("participant is not marked synthetic")
            participant_id = participant["participantId"]
            if participant_id in seen_ids:
                raise ValueError("duplicate synthetic participant ID")
            seen_ids.add(participant_id)
            weeks = [check_in["week"] for check_in in participant["checkIns"]]
            if len(weeks) != len(set(weeks)):
                raise ValueError("duplicate synthetic participant/week")
            for check_in in participant["checkIns"]:
                if check_in["contractVersion"] != participant["contractVersion"]:
                    raise ValueError("check-in version does not match its synthetic participant")
                validate_check_in(check_in)
            for submitted_assessment in participant["assessments"]:
                AssessmentSubmission.model_validate(submitted_assessment)
            assessment_types = [row["assessmentType"] for row in participant["assessments"]]
            if not assessment_types or assessment_types[0] != "baseline":
                raise ValueError("every synthetic participant requires a baseline assessment")
            if len(assessment_types) != len(set(assessment_types)):
                raise ValueError("duplicate synthetic assessment type")
            follow_up_at = next(
                (
                    datetime.fromisoformat(row["completedAt"].replace("Z", "+00:00"))
                    for row in participant["assessments"]
                    if row["assessmentType"] == "follow_up"
                ),
                None,
            )
            if follow_up_at is not None and any(
                datetime.fromisoformat(row["completedAt"].replace("Z", "+00:00")) >= follow_up_at
                for row in participant["checkIns"]
            ):
                raise ValueError("synthetic check-in occurs at or after follow-up")
            if participant["withdrawalState"] == "deleted" and follow_up_at is not None:
                raise ValueError("withdrawn synthetic participant must not have a follow-up")
            actual_gap = intention_action_gap(participant["checkIns"])
            if actual_gap != participant["expectedFeatures"]["intentionActionGap"]:
                raise ValueError("synthetic feature expectation does not match source rows")
            if actual_gap is None:
                missing_features += 1
            if len(participant["assessments"]) < 2:
                attrited += 1
            elif actual_gap is not None:
                baseline = sum(
                    item["responseCode"] for item in participant["assessments"][0]["responses"]
                )
                follow_up = sum(
                    item["responseCode"] for item in participant["assessments"][1]["responses"]
                )
                pairs.append((actual_gap, follow_up - baseline))
        scenario = metadata["scenario"]
        slope = _slope(pairs)
        if scenario == "null" and slope is not None and abs(slope) > 0.01:
            raise ValueError("null scenario does not preserve a null generated gap effect")
        if scenario in {"weak_effect", "known_effect", "confounded"} and (
            slope is None or slope <= 0
        ):
            raise ValueError(f"{scenario} scenario does not preserve its expected direction")
        summaries[scenario] = {
            "participants": len(cohort["participants"]),
            "analyticParticipants": len(pairs),
            "missingGapFeatures": missing_features,
            "attritedParticipants": attrited,
            "observedResidualSlope": slope,
        }
    return summaries
