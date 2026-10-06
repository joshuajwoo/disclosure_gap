"""Feature-quality summaries that preserve insufficient-data states."""

from __future__ import annotations

from typing import Any

import polars as pl

FEATURE_COLUMNS = (
    "intention_action_gap",
    "audience_asymmetry",
    "topic_sensitivity_gap",
    "anticipated_judgment_rate",
    "support_mismatch_rate",
    "within_person_comfort_variability",
)


def feature_quality_report(features: pl.DataFrame) -> dict[str, Any]:
    total = features.height
    coverage = {}
    for column in FEATURE_COLUMNS:
        observed = features[column].drop_nulls()
        coverage[column] = {
            "available": observed.len(),
            "missing": features[column].null_count(),
            "mean": observed.mean(),
            "minimum": observed.min(),
            "maximum": observed.max(),
        }
    denominators = features["eligible_gap_denominator"].to_list()
    versions = sorted(set(features["source_contract_versions"].to_list()))
    return {
        "featureContractVersion": "1.0.0-draft",
        "participants": total,
        "coverage": coverage,
        "gapDenominator": {
            "minimum": min(denominators, default=None),
            "maximum": max(denominators, default=None),
        },
        "minimumCheckInExclusions": sum(
            value == "fewer_than_minimum_check_ins"
            for value in features["gap_exclusion_reason"].to_list()
        ),
        "sourceContractVersionCombinations": versions,
        "availabilityBySourceVersion": {
            version: {
                "participants": subset.height,
                "gapAvailable": subset["intention_action_gap"].drop_nulls().len(),
            }
            for version in versions
            if (subset := features.filter(pl.col("source_contract_versions") == version)).height
        },
        "unsupportedMappings": [],
    }
