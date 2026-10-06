from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import polars as pl
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from apps.api.disclosure_gap_api.models import (
    Assessment,
    Base,
    CheckIn,
    ExportAudit,
    Participant,
)
from research.analysis import (
    analysis_suite,
    assert_real_analysis_allowed,
    predictive_modeling_gate,
)
from research.build_report import SYNTHETIC_LABEL, build_report
from research.etl import AnalysisTables, load_export
from research.export import (
    PROHIBITED_FIELDS,
    create_restricted_export,
    validate_export,
    write_synthetic_export,
)
from research.features import build_features
from research.quality import feature_quality_report
from research.synthetic import generate_all


def test_restricted_export_uses_fresh_ids_excludes_deleted_and_records_audit(
    tmp_path: Path,
) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    start = datetime(2026, 1, 5, 9, tzinfo=UTC)
    with Session(engine) as session:
        active = Participant(
            id="00000000-0000-0000-0000-000000000001",
            age_band="18_19",
            contract_version="1.0.0-draft",
            withdrawal_state="active",
            created_at=start,
        )
        deleted = Participant(
            id="00000000-0000-0000-0000-000000000002",
            age_band="20_22",
            contract_version="1.0.0-draft",
            withdrawal_state="deleted",
            created_at=start,
        )
        session.add_all([active, deleted])
        session.add(
            Assessment(
                participant_id=active.id,
                assessment_type="baseline",
                instrument_name="apa_dsm5tr_sad_adult",
                instrument_version="DSM-5-TR-2022",
                language="en",
                contract_version="1.0.0-draft",
                item_responses=[],
                total_score=12,
                completed_at=start,
            )
        )
        session.add(
            CheckIn(
                participant_id=active.id,
                week=1,
                contract_version="1.0.0-draft",
                wanted_to_share="no",
                completed_at=start + timedelta(days=1),
            )
        )
        session.commit()
        with pytest.raises(PermissionError):
            create_restricted_export(
                session, tmp_path / "denied", authorized_role="viewer", approval_id="A-1"
            )
        manifest = create_restricted_export(
            session,
            tmp_path / "approved",
            authorized_role="research_exporter",
            approval_id="A-1",
        )
        assert manifest["rowCounts"]["participants"] == 1
        assert session.scalar(select(func.count()).select_from(ExportAudit)) == 1
    tables = validate_export(tmp_path / "approved")
    exported_id = tables["participants"]["analysis_id"][0]
    assert exported_id not in {
        "00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000002",
    }
    assert not any(PROHIBITED_FIELDS & set(frame.columns) for frame in tables.values())


def test_synthetic_export_etl_and_tamper_detection(tmp_path: Path) -> None:
    export_dir = tmp_path / "export"
    manifest = write_synthetic_export(generate_all(seed=11, size=8), export_dir)
    tables = load_export(export_dir)
    assert manifest["synthetic"] is True
    assert set(manifest["sourceContractVersions"]) == {
        "1.0.0-draft",
        "1.1.0-fixture",
    }
    assert tables.participants.height > 0
    check_path = export_dir / "check_ins.parquet"
    check_path.write_bytes(check_path.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="digest"):
        validate_export(export_dir)


def _rewrite_export_table(export_dir: Path, name: str, frame: pl.DataFrame) -> None:
    path = export_dir / f"{name}.parquet"
    frame.write_parquet(path)
    manifest_path = export_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["rowCounts"][name] = frame.height
    digests = {
        table: hashlib.sha256((export_dir / filename).read_bytes()).hexdigest()
        for table, filename in manifest["tables"].items()
    }
    manifest["artifactDigest"] = hashlib.sha256(
        json.dumps(digests, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("prohibited", "prohibited field"),
        ("orphan", "orphan row"),
        ("duplicate", "duplicate participant/week"),
        ("invalid_value", "invalid wanted_to_share"),
        ("late", "at or after follow-up"),
    ],
)
def test_export_validation_rejects_structural_and_temporal_failures(
    tmp_path: Path, case: str, message: str
) -> None:
    export_dir = tmp_path / case
    write_synthetic_export(generate_all(seed=12, size=8), export_dir)
    table_name = "participants" if case == "prohibited" else "check_ins"
    frame = pl.read_parquet(export_dir / f"{table_name}.parquet")
    if case == "prohibited":
        frame = frame.with_columns(pl.lit("secret").alias("participant_id"))
    elif case == "orphan":
        frame = (
            frame.with_row_index()
            .with_columns(
                pl.when(pl.col("index") == 0)
                .then(pl.lit("orphan-analysis-id"))
                .otherwise(pl.col("analysis_id"))
                .alias("analysis_id")
            )
            .drop("index")
        )
    elif case == "duplicate":
        frame = pl.concat([frame, frame.head(1)])
    elif case == "invalid_value":
        frame = (
            frame.with_row_index()
            .with_columns(
                pl.when(pl.col("index") == 0)
                .then(pl.lit("invalid"))
                .otherwise(pl.col("wanted_to_share"))
                .alias("wanted_to_share")
            )
            .drop("index")
        )
    else:
        frame = (
            frame.with_row_index()
            .with_columns(
                pl.when(pl.col("index") == 0)
                .then(pl.lit(100.0))
                .otherwise(pl.col("study_day"))
                .alias("study_day")
            )
            .drop("index")
        )
    _rewrite_export_table(export_dir, table_name, frame)
    with pytest.raises(ValueError, match=message):
        validate_export(export_dir)


def test_feature_formulas_missingness_and_follow_up_cutoff() -> None:
    participants = pl.DataFrame(
        [
            {
                "analysis_id": "p1",
                "scenario": "fixture",
                "age_band": "18_19",
                "contract_version": "1.0.0-draft",
                "study_start": "2026-01-01T00:00:00Z",
            },
            {
                "analysis_id": "p2",
                "scenario": "fixture",
                "age_band": "20_22",
                "contract_version": "1.0.0-draft",
                "study_start": "2026-01-01T00:00:00Z",
            },
        ]
    )
    contexts = pl.DataFrame(
        [
            {
                "analysis_id": "p1",
                "contract_version": "1.0.0-draft",
                "support_confidence": 3,
                "support_confidence_nonresponse": None,
                "everyday_comfort": 4,
                "everyday_comfort_nonresponse": None,
                "insecurity_comfort": 2,
                "insecurity_comfort_nonresponse": None,
                "study_day": 0.0,
            }
        ]
    )
    assessments = pl.DataFrame(
        [
            {
                "analysis_id": "p1",
                "assessment_type": "baseline",
                "contract_version": "1.0.0-draft",
                "instrument_version": "DSM-5-TR-2022",
                "total_score": 10,
                "study_day": 0.0,
            },
            {
                "analysis_id": "p1",
                "assessment_type": "follow_up",
                "contract_version": "1.0.0-draft",
                "instrument_version": "DSM-5-TR-2022",
                "total_score": 14,
                "study_day": 29.0,
            },
            {
                "analysis_id": "p2",
                "assessment_type": "baseline",
                "contract_version": "1.0.0-draft",
                "instrument_version": "DSM-5-TR-2022",
                "total_score": 9,
                "study_day": 0.0,
            },
        ]
    )
    base = {
        "analysis_id": "p1",
        "contract_version": "1.0.0-draft",
        "wanted_to_share": "yes",
        "expected_comfort_nonresponse": None,
        "support_confidence_nonresponse": None,
        "concern_category": "everyday",
    }
    check_ins = pl.DataFrame(
        [
            base
            | {
                "week": 1,
                "intended_audience": "friend",
                "sharing_action": "chose_private",
                "expected_comfort": 1,
                "anticipated_judgment": "yes",
                "support_confidence": 1,
                "study_day": 7.0,
            },
            base
            | {
                "week": 2,
                "intended_audience": "family",
                "sharing_action": "shared",
                "expected_comfort": 2,
                "anticipated_judgment": "no",
                "support_confidence": 4,
                "study_day": 14.0,
            },
            base
            | {
                "week": 3,
                "intended_audience": "friend",
                "sharing_action": "shared",
                "expected_comfort": 3,
                "anticipated_judgment": "prefer_not_to_answer",
                "support_confidence": 2,
                "study_day": 21.0,
            },
            base
            | {
                "week": 4,
                "intended_audience": "family",
                "sharing_action": "chose_private",
                "expected_comfort": 5,
                "anticipated_judgment": "yes",
                "support_confidence": 1,
                "study_day": 30.0,
            },
        ]
    )
    tables = AnalysisTables({}, participants, contexts, assessments, check_ins)
    features = build_features(tables)
    first = features.filter(pl.col("analysis_id") == "p1").row(0, named=True)
    second = features.filter(pl.col("analysis_id") == "p2").row(0, named=True)
    assert first["completed_check_ins"] == 3
    assert first["intention_action_gap"] == pytest.approx(1 / 3)
    assert first["audience_asymmetry"] == pytest.approx(0.0)
    assert first["topic_sensitivity_gap"] == 2.0
    assert first["anticipated_judgment_rate"] == 0.5
    assert first["support_mismatch_rate"] == pytest.approx(2 / 3)
    assert first["within_person_comfort_variability"] == 1.0
    assert second["intention_action_gap"] is None
    assert second["gap_exclusion_reason"] == "fewer_than_minimum_check_ins"
    quality = feature_quality_report(features)
    assert quality["coverage"]["intention_action_gap"]["available"] == 1
    assert quality["coverage"]["intention_action_gap"]["missing"] == 1


def test_analysis_gates_and_one_command_report(tmp_path: Path) -> None:
    result = build_report(tmp_path / "report", seed=77, size=8)
    assert result["label"] == SYNTHETIC_LABEL
    assert result["scenarios"] == [
        "attrition",
        "confounded",
        "known_effect",
        "missingness",
        "null",
        "weak_effect",
    ]
    report = (tmp_path / "report/report.md").read_text(encoding="utf-8")
    assert SYNTHETIC_LABEL in report
    assert "No real participant data were analyzed" in report
    analysis = json.loads((tmp_path / "report/analysis.json").read_text(encoding="utf-8"))
    assert analysis["known_effect"]["predictiveModeling"]["status"] == "not_performed"
    assert predictive_modeling_gate()["status"] == "not_performed"
    with pytest.raises(PermissionError):
        assert_real_analysis_allowed({"synthetic": True}, approved=True)
    suite = analysis_suite(pl.read_parquet(tmp_path / "report/features.parquet"))
    assert suite["primaryExploratory"]["status"] == "estimated"
