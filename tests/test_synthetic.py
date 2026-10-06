import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from apps.api.disclosure_gap_api.config import Settings
from research.data_boundary import DataBoundaryError, assert_safe_generated_output
from research.synthetic import SCENARIOS, generate_all, validate_dataset

ROOT = Path(__file__).parents[1]


def test_generation_is_deterministic_and_exercises_all_scenarios() -> None:
    first = generate_all(seed=42, size=12)
    second = generate_all(seed=42, size=12)
    assert first == second
    assert [cohort["metadata"]["scenario"] for cohort in first["cohorts"]] == list(SCENARIOS)
    summaries = validate_dataset(first)
    assert summaries["null"]["observedResidualSlope"] == pytest.approx(0.0)
    assert summaries["known_effect"]["observedResidualSlope"] > 4
    assert summaries["missingness"]["missingGapFeatures"] > 0
    assert summaries["attrition"]["attritedParticipants"] > 0


def test_generator_supports_both_explicit_check_in_versions() -> None:
    dataset = generate_all(seed=7, size=8)
    versions = {
        participant["contractVersion"]
        for cohort in dataset["cohorts"]
        for participant in cohort["participants"]
    }
    assert versions == {"1.0.0-draft", "1.1.0-fixture"}


def test_committed_edge_and_regression_fixtures_are_synthetic_and_reviewable() -> None:
    fixture_dir = ROOT / "tests/fixtures/synthetic"
    edge = json.loads((fixture_dir / "edge-cases.json").read_text(encoding="utf-8"))
    regression = json.loads((fixture_dir / "regression.json").read_text(encoding="utf-8"))
    assert edge["synthetic"] is True
    assert len(edge["cases"]) == 10
    assert regression["synthetic"] is True
    assert regression["expectedFeatures"][0]["intentionActionGap"] == 0.5
    assert regression["expectedReport"]["dataSourceLabel"].startswith("SYNTHETIC")

    actual_features = []
    for expected in regression["expectedFeatures"]:
        rows = [
            row for row in regression["checkIns"] if row["participant"] == expected["participant"]
        ]
        eligible = [row for row in rows if row["wanted"] == "yes"]
        gap = (
            sum(row["action"] in {"not_shared", "chose_private"} for row in eligible)
            / len(eligible)
            if eligible and len(rows) >= 3
            else None
        )
        actual_features.append(
            {
                "participant": expected["participant"],
                "completedCheckIns": len(rows),
                "intentionActionGap": gap,
                "exclusionReason": (
                    "fewer_than_3_check_ins"
                    if len(rows) < 3
                    else "no_eligible_wanted_weeks"
                    if not eligible
                    else None
                ),
            }
        )
    assert actual_features == regression["expectedFeatures"]


def test_public_boundaries_reject_real_data_configuration_and_output_paths(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="must remain synthetic-only"):
        Settings(
            app_env="public-demo",
            allow_real_participant_data=True,
            real_data_readiness_approved=True,
        )
    with pytest.raises(DataBoundaryError, match="must stay under data/synthetic"):
        assert_safe_generated_output(tmp_path / "public-records.json", ROOT)
    assert not list((ROOT / "apps/web").glob("**/*participant*.json"))
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/" in gitignore
    assert "exports/" in gitignore
