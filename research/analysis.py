"""Transparent validation analyses; prediction is deliberately out of scope."""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl


def exploratory_regression(
    features: pl.DataFrame, *, include_leakage_sensitive: bool = False
) -> dict[str, Any]:
    columns = ["intention_action_gap", "baseline_score", "follow_up_score"]
    if include_leakage_sensitive:
        columns.append("anticipated_judgment_rate")
    complete = features.drop_nulls(columns)
    predictor_names = ["intention_action_gap", "baseline_score"]
    if include_leakage_sensitive:
        predictor_names.append("anticipated_judgment_rate")
    minimum = len(predictor_names) + 3
    if complete.height < minimum:
        return {
            "status": "insufficient_data",
            "n": complete.height,
            "minimumRequired": minimum,
            "predictors": predictor_names,
        }
    x = np.asarray(complete.select(predictor_names).rows(), dtype=float)
    y = np.asarray(complete["follow_up_score"].to_list(), dtype=float)
    design = np.column_stack((np.ones(complete.height), x))
    coefficients, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
    fitted = design @ coefficients
    residuals = y - fitted
    degrees_of_freedom = complete.height - design.shape[1]
    residual_variance = float((residuals @ residuals) / degrees_of_freedom)
    covariance = residual_variance * np.linalg.pinv(design.T @ design)
    index = predictor_names.index("intention_action_gap") + 1
    standard_error = float(np.sqrt(covariance[index, index]))
    coefficient = float(coefficients[index])
    total_variance = float(((y - y.mean()) ** 2).sum())
    residual_sum = float((residuals**2).sum())
    return {
        "status": "estimated",
        "n": complete.height,
        "predictors": predictor_names,
        "gapCoefficient": coefficient,
        "gapConfidenceInterval95": [
            coefficient - 1.96 * standard_error,
            coefficient + 1.96 * standard_error,
        ],
        "rSquared": 1 - residual_sum / total_variance if total_variance else None,
        "interpretation": "synthetic software validation only"
        if "scenario" in features.columns
        else "exploratory association",
    }


def analysis_suite(features: pl.DataFrame) -> dict[str, Any]:
    thresholds: dict[str, dict[str, Any]] = {}
    for threshold in (2, 3, 4):
        eligible = features.filter(pl.col("completed_check_ins") >= threshold)
        thresholds[str(threshold)] = exploratory_regression(eligible)
    base = exploratory_regression(features)
    overlap = exploratory_regression(features, include_leakage_sensitive=True)
    complete = features.drop_nulls(["intention_action_gap", "baseline_score", "follow_up_score"])
    trimmed = complete
    if complete.height >= 10:
        changes = complete.with_columns(
            (pl.col("follow_up_score") - pl.col("baseline_score")).alias("change")
        ).sort("change")
        trimmed = changes.slice(1, changes.height - 2)
    followed = features.filter(pl.col("follow_up_available"))
    attrited = features.filter(~pl.col("follow_up_available"))

    def baseline_mean(frame: pl.DataFrame) -> float | None:
        value = frame["baseline_score"].drop_nulls().mean()
        return float(value) if isinstance(value, int | float) else None

    return {
        "descriptive": {
            "participants": features.height,
            "followUpAvailable": int(features["follow_up_available"].sum()),
            "gapAvailable": features["intention_action_gap"].drop_nulls().len(),
            "gapMissing": features["intention_action_gap"].null_count(),
            "featureContractVersions": sorted(set(features["feature_contract_version"].to_list())),
            "sourceContractVersionCombinations": sorted(
                set(features["source_contract_versions"].to_list())
            ),
        },
        "missingnessAndAttrition": {
            "followedParticipants": followed.height,
            "attritedParticipants": attrited.height,
            "followedBaselineMean": baseline_mean(followed),
            "attritedBaselineMean": baseline_mean(attrited),
            "note": "Descriptive synthetic pipeline check; no missing values are coerced to zero.",
        },
        "primaryExploratory": base,
        "leakageSensitivity": {
            "prespecifiedWithoutOverlap": base,
            "augmentedWithFlaggedJudgmentFeature": overlap,
        },
        "minimumCheckInThresholds": thresholds,
        "influentialObservationCheck": exploratory_regression(trimmed),
        "predictiveModeling": predictive_modeling_gate(),
        "subgroupChecks": privacy_safe_subgroup_check(features),
    }


def predictive_modeling_gate(*, justification: str | None = None) -> dict[str, str]:
    if not justification:
        return {
            "status": "not_performed",
            "reason": (
                "No documented sample-size and use-case justification; prediction is outside "
                "core scope."
            ),
        }
    return {"status": "review_required", "reason": justification}


def privacy_safe_subgroup_check(
    features: pl.DataFrame, *, approved_real_data: bool = False, minimum_cell_size: int = 10
) -> dict[str, Any]:
    if "scenario" in features.columns or not approved_real_data:
        return {
            "status": "omitted",
            "reason": (
                "Subgroup checks require approved real data, adequate power, and "
                "disclosure-safe cells."
            ),
        }
    return {"status": "eligible_for_manual_review", "minimumCellSize": minimum_cell_size}


def assert_real_analysis_allowed(manifest: dict[str, Any], *, approved: bool) -> None:
    if manifest.get("synthetic") is not False or not approved:
        raise PermissionError(
            "optional real-data analysis requires a non-synthetic approved export"
        )
