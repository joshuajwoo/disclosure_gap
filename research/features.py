"""Feature contract 1.0.0-draft implemented without future-data leakage."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any

import polars as pl

from research.etl import AnalysisTables

FEATURE_CONTRACT_VERSION = "1.0.0-draft"


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def build_features(tables: AnalysisTables, *, minimum_check_ins: int = 3) -> pl.DataFrame:
    assessments: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in tables.assessments.to_dicts():
        assessments[row["analysis_id"]][row["assessment_type"]] = row
    contexts = {row["analysis_id"]: row for row in tables.baseline_contexts.to_dicts()}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in tables.check_ins.to_dicts():
        follow_up = assessments[row["analysis_id"]].get("follow_up")
        if follow_up is None or row["study_day"] < follow_up["study_day"]:
            grouped[row["analysis_id"]].append(row)

    output: list[dict[str, Any]] = []
    for participant in tables.participants.to_dicts():
        analysis_id = participant["analysis_id"]
        rows = grouped[analysis_id]
        eligible = [
            row
            for row in rows
            if row["wanted_to_share"] == "yes"
            and row["sharing_action"] in {"shared", "not_shared", "chose_private"}
        ]
        if len(rows) < minimum_check_ins:
            gap = None
            reason = "fewer_than_minimum_check_ins"
        elif not eligible:
            gap = None
            reason = "no_eligible_wanted_weeks"
        else:
            gap = sum(
                row["sharing_action"] in {"not_shared", "chose_private"} for row in eligible
            ) / len(eligible)
            reason = None
        friend = [
            float(row["expected_comfort"])
            for row in rows
            if row["intended_audience"] == "friend" and row["expected_comfort"] is not None
        ]
        family = [
            float(row["expected_comfort"])
            for row in rows
            if row["intended_audience"] == "family" and row["expected_comfort"] is not None
        ]
        audience_asymmetry = (
            _mean(friend) - _mean(family) if friend and family else None  # type: ignore[operator]
        )
        judgment = [
            row["anticipated_judgment"]
            for row in rows
            if row["anticipated_judgment"] in {"yes", "no"}
        ]
        supported = [
            row
            for row in rows
            if row["wanted_to_share"] == "yes" and row["support_confidence"] is not None
        ]
        comfort = [
            float(row["expected_comfort"]) for row in rows if row["expected_comfort"] is not None
        ]
        context = contexts.get(analysis_id, {})
        everyday = context.get("everyday_comfort")
        insecurity = context.get("insecurity_comfort")
        versions = sorted({row["contract_version"] for row in rows})
        baseline = assessments[analysis_id].get("baseline", {}).get("total_score")
        follow_up = assessments[analysis_id].get("follow_up", {}).get("total_score")
        output.append(
            {
                "analysis_id": analysis_id,
                "scenario": participant["scenario"],
                "feature_contract_version": FEATURE_CONTRACT_VERSION,
                "source_contract_versions": ",".join(versions),
                "completed_check_ins": len(rows),
                "eligible_gap_denominator": len(eligible),
                "intention_action_gap": gap,
                "gap_exclusion_reason": reason,
                "audience_asymmetry": audience_asymmetry,
                "topic_sensitivity_gap": (
                    float(everyday - insecurity)
                    if isinstance(everyday, int) and isinstance(insecurity, int)
                    else None
                ),
                "anticipated_judgment_rate": (
                    sum(value == "yes" for value in judgment) / len(judgment) if judgment else None
                ),
                "support_mismatch_rate": (
                    sum(row["support_confidence"] <= 2 for row in supported) / len(supported)
                    if supported
                    else None
                ),
                "within_person_comfort_variability": (
                    statistics.stdev(comfort) if len(comfort) >= 2 else None
                ),
                "baseline_score": baseline,
                "follow_up_score": follow_up,
                "follow_up_available": follow_up is not None,
            }
        )
    frame = pl.DataFrame(output)
    numeric = [
        "intention_action_gap",
        "audience_asymmetry",
        "topic_sensitivity_gap",
        "anticipated_judgment_rate",
        "support_mismatch_rate",
        "within_person_comfort_variability",
    ]
    for column in numeric:
        if column in frame.columns and frame[column].dtype == pl.Null:
            frame = frame.with_columns(pl.lit(None, dtype=pl.Float64).alias(column))
    if any(
        value is not None and (not math.isfinite(value))
        for column in numeric
        for value in frame[column].to_list()
    ):
        raise ValueError("non-finite engineered feature")
    return frame
