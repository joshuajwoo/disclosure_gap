"""Restricted, versioned research exports with a synthetic adapter."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.disclosure_gap_api.models import (
    Assessment,
    BaselineContext,
    CheckIn,
    ExportAudit,
    Participant,
)

EXPORT_VERSION = "1.0.0"
AUTHORIZED_ROLE = "research_exporter"
TABLE_FIELDS: dict[str, tuple[str, ...]] = {
    "participants": (
        "analysis_id",
        "scenario",
        "age_band",
        "contract_version",
    ),
    "baseline_contexts": (
        "analysis_id",
        "contract_version",
        "support_confidence",
        "support_confidence_nonresponse",
        "everyday_comfort",
        "everyday_comfort_nonresponse",
        "insecurity_comfort",
        "insecurity_comfort_nonresponse",
        "study_day",
    ),
    "assessments": (
        "analysis_id",
        "assessment_type",
        "contract_version",
        "instrument_version",
        "total_score",
        "study_day",
    ),
    "check_ins": (
        "analysis_id",
        "week",
        "contract_version",
        "wanted_to_share",
        "intended_audience",
        "sharing_action",
        "expected_comfort",
        "expected_comfort_nonresponse",
        "anticipated_judgment",
        "support_confidence",
        "support_confidence_nonresponse",
        "concern_category",
        "study_day",
    ),
}
PROHIBITED_FIELDS = {
    "participant_id",
    "session_token",
    "session_token_hash",
    "recovery_code",
    "recovery_code_hash",
    "idempotency_key",
    "payload_hash",
    "completed_at",
    "created_at",
    "deleted_at",
}


def schema_fingerprint() -> str:
    encoded = json.dumps(TABLE_FIELDS, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _day(value: datetime, start: datetime) -> float:
    return round((value - start).total_seconds() / 86400, 6)


def _split_ordinal(value: Any) -> tuple[int | None, str | None]:
    return (
        (value, None) if isinstance(value, int) and not isinstance(value, bool) else (None, value)
    )


def _write_bundle(
    tables: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    *,
    synthetic: bool,
    approval_id: str,
    role: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    digests: dict[str, str] = {}
    filenames: dict[str, str] = {}
    for name, fields in TABLE_FIELDS.items():
        path = output_dir / f"{name}.parquet"
        rows = tables[name]
        frame = (
            pl.DataFrame(rows).select(list(fields))
            if rows
            else pl.DataFrame({field: [] for field in fields})
        )
        frame.write_parquet(path)
        filenames[name] = path.name
        digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    versions = sorted(
        {
            str(row["contract_version"])
            for rows in tables.values()
            for row in rows
            if row.get("contract_version")
        }
    )
    manifest = {
        "exportVersion": EXPORT_VERSION,
        "schemaFingerprint": schema_fingerprint(),
        "synthetic": synthetic,
        "createdAt": "2026-01-01T00:00:00Z" if synthetic else _iso(datetime.now(UTC)),
        "sourceContractVersions": versions,
        "rowCounts": {name: len(rows) for name, rows in tables.items()},
        "tables": filenames,
        "provenance": {
            "workflow": "synthetic-generator" if synthetic else "restricted-manual",
            "approvalId": approval_id,
            "createdByRole": role,
        },
        "artifactDigest": hashlib.sha256(
            json.dumps(digests, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validate_export(output_dir)
    return manifest


def synthetic_tables(dataset: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    if dataset.get("metadata", {}).get("synthetic") is not True:
        raise ValueError("synthetic export requires an explicitly synthetic dataset")
    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in TABLE_FIELDS}
    for cohort in dataset["cohorts"]:
        scenario = cohort["metadata"]["scenario"]
        for participant in cohort["participants"]:
            if participant["withdrawalState"] != "active":
                continue
            source_id = participant["participantId"]
            analysis_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"analysis:{source_id}"))
            baseline = next(
                row for row in participant["assessments"] if row["assessmentType"] == "baseline"
            )
            start = _dt(baseline["completedAt"])
            tables["participants"].append(
                {
                    "analysis_id": analysis_id,
                    "scenario": scenario,
                    "age_band": participant["ageBand"],
                    "contract_version": participant["contractVersion"],
                }
            )
            context = participant["baselineContext"]
            support, support_nr = _split_ordinal(context["supportConfidence"])
            everyday, everyday_nr = _split_ordinal(context["everydayComfort"])
            insecurity, insecurity_nr = _split_ordinal(context["insecurityComfort"])
            tables["baseline_contexts"].append(
                {
                    "analysis_id": analysis_id,
                    "contract_version": context["contractVersion"],
                    "support_confidence": support,
                    "support_confidence_nonresponse": support_nr,
                    "everyday_comfort": everyday,
                    "everyday_comfort_nonresponse": everyday_nr,
                    "insecurity_comfort": insecurity,
                    "insecurity_comfort_nonresponse": insecurity_nr,
                    "study_day": _day(_dt(context["completedAt"]), start),
                }
            )
            for row in participant["assessments"]:
                score_values = [item["responseCode"] for item in row["responses"]]
                score = sum(value for value in score_values if isinstance(value, int))
                tables["assessments"].append(
                    {
                        "analysis_id": analysis_id,
                        "assessment_type": row["assessmentType"],
                        "contract_version": row["contractVersion"],
                        "instrument_version": row["instrumentVersion"],
                        "total_score": score,
                        "study_day": _day(_dt(row["completedAt"]), start),
                    }
                )
            for row in participant["checkIns"]:
                comfort, comfort_nr = _split_ordinal(row.get("expectedComfort"))
                support, support_nr = _split_ordinal(row.get("supportConfidence"))
                tables["check_ins"].append(
                    {
                        "analysis_id": analysis_id,
                        "week": row["week"],
                        "contract_version": row["contractVersion"],
                        "wanted_to_share": row["wantedToShare"],
                        "intended_audience": row.get("intendedAudience"),
                        "sharing_action": row.get("sharingAction"),
                        "expected_comfort": comfort,
                        "expected_comfort_nonresponse": comfort_nr,
                        "anticipated_judgment": row.get("anticipatedJudgment"),
                        "support_confidence": support,
                        "support_confidence_nonresponse": support_nr,
                        "concern_category": row.get("concernCategory"),
                        "study_day": _day(_dt(row["completedAt"]), start),
                    }
                )
    return tables


def write_synthetic_export(dataset: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    return _write_bundle(
        synthetic_tables(dataset),
        output_dir,
        synthetic=True,
        approval_id="synthetic-not-applicable",
        role="synthetic_generator",
    )


def create_restricted_export(
    session: Session, output_dir: Path, *, authorized_role: str, approval_id: str
) -> dict[str, Any]:
    if authorized_role != AUTHORIZED_ROLE or not approval_id.strip():
        raise PermissionError("manual export requires the research_exporter role and approval ID")
    participants = session.scalars(
        select(Participant).where(Participant.withdrawal_state == "active")
    ).all()
    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in TABLE_FIELDS}
    for participant in participants:
        analysis_id = str(uuid.uuid4())
        start = participant.created_at
        tables["participants"].append(
            {
                "analysis_id": analysis_id,
                "scenario": None,
                "age_band": participant.age_band,
                "contract_version": participant.contract_version,
            }
        )
        context = session.scalar(
            select(BaselineContext).where(BaselineContext.participant_id == participant.id)
        )
        if context:
            tables["baseline_contexts"].append(
                {
                    "analysis_id": analysis_id,
                    "contract_version": context.contract_version,
                    "support_confidence": context.support_confidence,
                    "support_confidence_nonresponse": context.support_confidence_nonresponse,
                    "everyday_comfort": context.everyday_comfort,
                    "everyday_comfort_nonresponse": context.everyday_comfort_nonresponse,
                    "insecurity_comfort": context.insecurity_comfort,
                    "insecurity_comfort_nonresponse": context.insecurity_comfort_nonresponse,
                    "study_day": _day(context.completed_at, start),
                }
            )
        for assessment_row in session.scalars(
            select(Assessment).where(Assessment.participant_id == participant.id)
        ):
            tables["assessments"].append(
                {
                    "analysis_id": analysis_id,
                    "assessment_type": assessment_row.assessment_type,
                    "contract_version": assessment_row.contract_version,
                    "instrument_version": assessment_row.instrument_version,
                    "total_score": assessment_row.total_score,
                    "study_day": _day(assessment_row.completed_at, start),
                }
            )
        for check_in_row in session.scalars(
            select(CheckIn).where(CheckIn.participant_id == participant.id)
        ):
            tables["check_ins"].append(
                {
                    "analysis_id": analysis_id,
                    "week": check_in_row.week,
                    "contract_version": check_in_row.contract_version,
                    "wanted_to_share": check_in_row.wanted_to_share,
                    "intended_audience": check_in_row.intended_audience,
                    "sharing_action": check_in_row.sharing_action,
                    "expected_comfort": check_in_row.expected_comfort,
                    "expected_comfort_nonresponse": check_in_row.expected_comfort_nonresponse,
                    "anticipated_judgment": check_in_row.anticipated_judgment,
                    "support_confidence": check_in_row.support_confidence,
                    "support_confidence_nonresponse": (check_in_row.support_confidence_nonresponse),
                    "concern_category": check_in_row.concern_category,
                    "study_day": _day(check_in_row.completed_at, start),
                }
            )
    manifest = _write_bundle(
        tables,
        output_dir,
        synthetic=False,
        approval_id=approval_id,
        role=authorized_role,
    )
    session.add(
        ExportAudit(
            export_version=EXPORT_VERSION,
            schema_fingerprint=manifest["schemaFingerprint"],
            created_by_role=authorized_role,
            source_contract_versions=manifest["sourceContractVersions"],
            row_counts=manifest["rowCounts"],
            provenance=manifest["provenance"],
            artifact_digest=manifest["artifactDigest"],
        )
    )
    session.commit()
    return manifest


def validate_export(output_dir: Path) -> dict[str, pl.DataFrame]:
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("exportVersion") != EXPORT_VERSION:
        raise ValueError("unsupported export version")
    if manifest.get("schemaFingerprint") != schema_fingerprint():
        raise ValueError("export schema fingerprint mismatch")
    actual_digests = {
        name: hashlib.sha256((output_dir / filename).read_bytes()).hexdigest()
        for name, filename in manifest["tables"].items()
    }
    actual_artifact_digest = hashlib.sha256(
        json.dumps(actual_digests, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if manifest.get("artifactDigest") != actual_artifact_digest:
        raise ValueError("export artifact digest mismatch")
    tables: dict[str, pl.DataFrame] = {}
    for name, expected in TABLE_FIELDS.items():
        frame = pl.read_parquet(output_dir / manifest["tables"][name])
        columns = set(frame.columns)
        if columns & PROHIBITED_FIELDS:
            raise ValueError(f"prohibited field in {name}")
        if tuple(frame.columns) != expected:
            raise ValueError(f"unexpected fields in {name}")
        if frame.height != manifest["rowCounts"][name]:
            raise ValueError(f"row count mismatch in {name}")
        tables[name] = frame
    ids = set(tables["participants"]["analysis_id"].to_list())
    if len(ids) != tables["participants"].height:
        raise ValueError("duplicate analysis ID")
    for name in ("baseline_contexts", "assessments", "check_ins"):
        if not set(tables[name]["analysis_id"].to_list()) <= ids:
            raise ValueError(f"orphan row in {name}")
    pairs = tables["check_ins"].select("analysis_id", "week").rows()
    if len(pairs) != len(set(pairs)):
        raise ValueError("duplicate participant/week")
    if any(day < 0 for day in tables["check_ins"]["study_day"].drop_nulls()):
        raise ValueError("check-in precedes study start")
    assessment_pairs = tables["assessments"].select("analysis_id", "assessment_type").rows()
    if len(assessment_pairs) != len(set(assessment_pairs)):
        raise ValueError("duplicate participant/assessment type")
    follow_up_days = {
        row["analysis_id"]: row["study_day"]
        for row in tables["assessments"].filter(pl.col("assessment_type") == "follow_up").to_dicts()
    }
    if any(
        row["analysis_id"] in follow_up_days
        and row["study_day"] >= follow_up_days[row["analysis_id"]]
        for row in tables["check_ins"].to_dicts()
    ):
        raise ValueError("check-in occurs at or after follow-up")
    allowed_wanted = {"yes", "no", "not_sure", "prefer_not_to_answer"}
    if not set(tables["check_ins"]["wanted_to_share"].drop_nulls().to_list()) <= allowed_wanted:
        raise ValueError("invalid wanted_to_share value")
    return tables
