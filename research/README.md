# Research pipeline

Owns synthetic cohort generation, de-identified export validation, ETL, feature engineering, optional exploratory analysis, figures, and reproducible reports. The default portfolio path validates pipeline behavior against declared synthetic scenarios; synthetic estimates are not findings about people. Analysis code must use only pre-follow-up predictors, preserve source contract versions, and preserve missing-value meanings.

`make synthetic` deterministically creates and validates null, weak-effect, known-effect, confounded, missingness, and attrition cohorts beneath ignored `data/synthetic/`. Scenario assumptions are documented in `docs/synthetic/scenarios.md`; committed edge and regression fixtures live in `tests/fixtures/synthetic/`.

`make report` performs the complete synthetic path: generation, contract and relationship validation, a versioned Parquet export, ETL, feature construction, scenario validation, descriptive quality summaries, uncertainty-bearing exploratory regressions, robustness checks, an aggregate figure, and a Markdown report beneath ignored `reports/generated/`. Every artifact is explicitly marked as synthetic pipeline validation.

The export contract is `1.0.0`. `research.export.create_restricted_export` requires the exact `research_exporter` role and an approval identifier, assigns fresh analysis IDs, excludes deleted participants and operational identifiers, records provenance in `export_audits`, and has no HTTP endpoint. `research.export.write_synthetic_export` is the separate deterministic adapter used by portfolio validation.

Features implement `packages/contracts/v1/features.json` using only check-ins before follow-up. Zero eligible weeks and inadequate completion produce missing values with reasons, never fabricated zeros. ETL accepts only explicitly supported source versions.

Predictive modeling is not performed without a documented sample-size and use-case review; any later evaluation must keep every record from one participant in the same fold and report uncertainty and calibration without clinical claims. Privacy-sensitive subgroup comparisons are omitted unless approved real data, power, and disclosure thresholds all permit them. The optional real-data analysis function also refuses synthetic or unapproved inputs; the repository’s real-data gate remains closed.
