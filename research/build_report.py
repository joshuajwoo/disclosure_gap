"""One-command deterministic rebuild of synthetic pipeline-validation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import polars as pl

from research.analysis import analysis_suite
from research.etl import load_export
from research.export import write_synthetic_export
from research.features import build_features
from research.quality import feature_quality_report
from research.synthetic import generate_all, validate_dataset

SYNTHETIC_LABEL = "SYNTHETIC — PIPELINE VALIDATION ONLY"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _plot(features: pl.DataFrame, output: Path) -> None:
    summaries = (
        features.with_columns(
            (pl.col("follow_up_score") - pl.col("baseline_score")).alias("score_change")
        )
        .group_by("scenario")
        .agg(
            pl.col("score_change").mean().alias("mean_change"),
            pl.col("score_change").std().alias("standard_deviation"),
            pl.col("score_change").count().alias("n"),
        )
        .sort("scenario")
    )
    figure, axis = plt.subplots(figsize=(9, 5))
    errors = [
        1.96 * row["standard_deviation"] / (row["n"] ** 0.5)
        if row["standard_deviation"] is not None and row["n"] > 1
        else 0
        for row in summaries.to_dicts()
    ]
    axis.bar(
        summaries["scenario"],
        summaries["mean_change"],
        yerr=errors,
        capsize=4,
        color="#3f6c67",
    )
    axis.axhline(0, color="#313a39", linewidth=0.8)
    axis.set_ylabel("Mean follow-up minus baseline score")
    axis.set_xlabel("Declared generator scenario")
    axis.set_title("Pipeline response across synthetic scenarios")
    axis.tick_params(axis="x", rotation=25)
    for index, row in enumerate(summaries.to_dicts()):
        axis.text(index, row["mean_change"], f" n={row['n']}", ha="center", va="bottom")
    figure.text(0.5, 0.01, SYNTHETIC_LABEL, ha="center", weight="bold", color="#9b2c2c")
    figure.tight_layout(rect=(0, 0.05, 1, 1))
    figure.savefig(output, dpi=160, metadata={"Title": SYNTHETIC_LABEL})
    plt.close(figure)


def build_report(output_dir: Path, *, seed: int = 20261004, size: int = 40) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset = generate_all(seed=seed, size=size)
    scenario_validation = validate_dataset(dataset)
    export_dir = output_dir / "validated-export"
    manifest = write_synthetic_export(dataset, export_dir)
    tables = load_export(export_dir)
    features = build_features(tables)
    features.write_parquet(output_dir / "features.parquet")
    quality = feature_quality_report(features)
    analyses = {
        scenario: analysis_suite(features.filter(pl.col("scenario") == scenario))
        for scenario in sorted(features["scenario"].unique().to_list())
    }
    _write_json(output_dir / "scenario-validation.json", scenario_validation)
    _write_json(output_dir / "feature-quality.json", quality)
    _write_json(output_dir / "analysis.json", analyses)
    _plot(features, output_dir / "scenario-summary.png")
    report = f"""# Disclosure Gap pipeline validation

> **{SYNTHETIC_LABEL}**

## Engineering purpose

This report verifies the versioned export, ETL, feature, and analysis code against
declared synthetic scenarios. It is not evidence about people and does not establish,
diagnose, or predict social anxiety. Choosing privacy can be healthy.

## Rebuild identity

- Seed: `{seed}`
- Generator participants per scenario: `{size}`
- Export version: `{manifest["exportVersion"]}`
- Feature contract: `1.0.0-draft`
- Exported analysis records: `{features.height}`

## Pipeline validation

All six declared scenarios—null, weak effect, known effect, confounded, missingness, and
attrition—passed contract and relational validation. Machine-readable scenario summaries
are in `scenario-validation.json`; feature coverage and explicit missing states are in
`feature-quality.json`; exploratory synthetic regression checks are in `analysis.json`.

The regression output reports coefficients and 95% intervals when enough complete rows
exist. Leakage-sensitive features are kept out of the prespecified model and shown only
as a sensitivity comparison. Threshold and influential-observation checks are included.
Predictive modeling and subgroup comparisons are explicitly omitted by gate.

## Optional exploratory real-data work

No real participant data were analyzed. That path remains closed until institutional
review, production security/readiness, explicit export approval, and adequate sample
justification are complete. If opened later, results must be reported separately as
exploratory associations with uncertainty—not causal, diagnostic, or therapeutic claims.

## Limitations

The synthetic assumptions were written by the project author and can only test software
behavior. Four weekly observations are sparse; audience-specific and variability features
are often unavailable. Synthetic estimates are expected products of the generator, not
discoveries.
"""
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    return {
        "label": SYNTHETIC_LABEL,
        "participants": features.height,
        "scenarios": sorted(analyses),
        "output": str(output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/generated"))
    parser.add_argument("--seed", type=int, default=20261004)
    parser.add_argument("--size", type=int, default=40)
    args = parser.parse_args()
    print(json.dumps(build_report(args.output, seed=args.seed, size=args.size), indent=2))


if __name__ == "__main__":
    main()
