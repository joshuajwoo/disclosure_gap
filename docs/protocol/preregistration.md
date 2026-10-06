# Optional exploratory analysis protocol

Status: draft for a possible institutionally approved real-data pilot; inactive while the project uses synthetic data. Version: 0.2.0, 2026-10-04.

This document preserves analysis decisions for a possible real-data extension. It is not evidence that recruitment is approved or necessary, and it does not turn synthetic output into empirical evidence. For synthetic cohorts, the same calculations are software tests against declared data-generating assumptions.

## Case-study question

Among consenting adults ages 18–22 in a possible approved pilot, how does a four-week intention–action gap relate to follow-up social-anxiety score after accounting for baseline score?

This question is motivated by personal interest and existing work on social anxiety, avoidance, self-disclosure, and help-seeking. It is not offered as a novel psychological theory. The analysis is observational and exploratory: it cannot establish causation, diagnosis, clinical utility, or that choosing privacy is unhealthy.

## Two distinct uses of the analysis code

1. **Default portfolio use—synthetic pipeline validation.** Run seeded null, weak-effect, known-effect, confounded, missingness, attrition, and contract-version scenarios. Compare results with generator expectations to find software or data-lineage errors. Any recovered coefficient describes a synthetic scenario, not people.
2. **Optional empirical use.** Only after all institutional, consent, security, and real-data-readiness gates are cleared, freeze this protocol before inspecting outcomes and apply it to an approved pilot. Report the result as exploratory unless a later design and sample-size justification supports stronger inference.

## Design and timing for an optional pilot

The proposed design is prospective and observational: baseline assessment; one structured check-in in each of four weekly windows; then follow-up assessment. Predictor check-ins must occur before the follow-up completion timestamp. No intervention is assigned.

Four weekly observations are intentionally modest and provide only a coarse behavioral summary. Relationship-specific contrasts and within-person variability will often be unavailable. The software must expose insufficient-data states instead of manufacturing a score.

## Population

- Inclusion: age 18–22 at consent; able to understand the approved consent language; affirmative, versioned consent; baseline assessment completed.
- Exclusion: ineligible age; no consent; synthetic/test record; duplicate enrollment detected under an approved procedure; follow-up completed before any eligible check-in; data withdrawn under the approved policy.
- No exclusion is based on social-anxiety score or a decision not to share.

## Measures

- Outcome: continuous 0–40 raw or prorated follow-up score from the APA DSM-5-TR Severity Measure for Social Anxiety Disorder—Adult, scored under `instrument-decision.md`.
- Baseline adjustment: raw or prorated score from the same instrument version and language at baseline.
- Primary case-study feature: eligible weeks where `wanted_to_share = yes` and `shared = no`, divided by eligible weeks where `wanted_to_share = yes`.
- Context variables: age band (18–19/20–22), baseline perceived support, and completed-check-in count. Their inclusion must be fixed before outcome access and kept small enough for the available sample.
- Secondary features: audience asymmetry, topic sensitivity gap, anticipated judgment rate, support mismatch, and within-person comfort variability. These remain exploratory.

“Prefer not to answer,” “not applicable,” missing, and zero are distinct. The gap is undefined when no completed check-in reports wanting to share. The default analysis requires at least three completed weekly check-ins; thresholds of two and four are robustness checks.

## Exploratory model

If a real pilot is approved and sufficiently sized, fit this transparent linear model:

`follow_up_score ~ baseline_score + intention_action_gap + age_band + baseline_support + completed_check_ins`

Report the gap coefficient, 95% confidence interval, diagnostics, analytic N, and missingness. Emphasize magnitude, uncertainty, and what the sample cannot resolve rather than a significance threshold. Do not select features or alter covariates after examining outcomes. If the feasible sample cannot support the model, restrict reporting to descriptive quality statistics and say so plainly.

## Missing data, leakage, and robustness

The optional model uses complete cases and requires a follow-up outcome. Report participant flow and, where disclosure risk permits, compare observed baseline variables for follow-up completers and non-completers. Never recode a missing desire or sharing response as “no.”

Keep the selected APA outcome questionnaire in a separate form. The overlap audit identifies anticipated judgment and general sharing comfort as conceptually adjacent to outcome items. Exclude those features from the case-study model and rerun the broader exclusions defined in the audit. Use only check-ins timestamped before follow-up and split any future resampling by participant, never by check-in.

Robustness checks cover minimum-completion thresholds of two and four, omission of completed-check-in count, sparse denominators, missing optional context variables, attrition, influential observations, and supported contract versions. These checks characterize fragility; they do not convert an exploratory pilot into confirmatory evidence.

## Feasibility before real recruitment

Before recruitment, document the smallest effect worth estimating, expected attrition, expected undefined-gap rate, covariate count, desired precision or power, and calculation method. If the approved and recruited sample cannot support the proposed model, do not make an association claim.

## Reporting commitments

Lead with the engineering purpose and separate pipeline-validation results from any empirical results. Report exclusions, attrition, feature coverage, denominator sizes, deviations, uncertainty, and null, negative, or uninformative outcomes. Suppress small cells under the approved disclosure rule. Do not claim causation, diagnosis, treatment utility, population prevalence, novelty, or that privacy is unhealthy.

## Change control

Synthetic fixtures and generator parameters may evolve through normal version control, but their expected results must remain explicit. Before any real outcome access, freeze and timestamp this protocol. Later amendments must identify the date, author, rationale, affected analyses, contract versions, and whether they occurred before or after outcome access.
