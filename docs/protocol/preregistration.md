# Preregistration draft

Status: draft for institutional review; synthetic/internal testing only. Version: 0.1.0, 2026-10-03.

## Question and hypothesis

Among consenting adults ages 18–22, is a larger four-week intention–action gap associated with a higher follow-up social-anxiety score after adjustment for baseline social-anxiety score?

The confirmatory hypothesis is that the coefficient for the intention–action gap will be positive in the prespecified linear regression. This is an associational, not causal, hypothesis.

## Design and timing

This is a prospective observational study: baseline assessment; one structured check-in in each of four weekly windows; then follow-up assessment. Predictor check-ins must occur before the follow-up completion timestamp. No intervention is assigned.

## Population

- Inclusion: age 18–22 at consent; able to understand the approved consent language; affirmative, versioned consent; baseline assessment completed.
- Exclusion: ineligible age; no consent; synthetic/test record; duplicate enrollment detected under an approved procedure; follow-up completed before any eligible check-in; data withdrawn under the approved policy.
- No exclusion will be based on a participant's social-anxiety score or decision not to share.

## Measures

- Primary outcome: continuous 0–40 raw/prorated follow-up score from the APA DSM-5-TR Severity Measure for Social Anxiety Disorder—Adult, scored under `instrument-decision.md`.
- Baseline adjustment: raw/prorated score from the same instrument version and language at baseline.
- Primary predictor: eligible weeks where `wanted_to_share = yes` and `shared = no`, divided by eligible weeks where `wanted_to_share = yes`.
- Prespecified context covariates: age band (18–19/20–22), baseline perceived-support item, and number of completed check-ins. These will be reconsidered in a blinded design review before data collection to avoid overfitting.
- Secondary features: audience asymmetry, topic sensitivity gap, anticipated judgment rate, support mismatch, and within-person comfort variability. These are exploratory unless separately powered and preregistered.

“Prefer not to answer,” “not applicable,” missing, and zero are distinct. A primary gap is undefined when no completed check-in reports wanting to share. The primary analysis requires at least three completed weekly check-ins; thresholds of two and four are sensitivity analyses.

## Confirmatory model

Fit ordinary least squares:

`follow_up_score ~ baseline_score + intention_action_gap + age_band + baseline_support + completed_check_ins`

Report the gap coefficient, 95% confidence interval, model diagnostics, analytic N, and missingness. The two-sided alpha is 0.05, but conclusions will emphasize magnitude and uncertainty rather than a thresholded p-value. No outcome-guided feature selection or covariate changes are permitted for the confirmatory result.

## Missing data and attrition

The primary analysis is complete-case for the prespecified model and requires a follow-up outcome. Report a participant flow diagram and compare observed baseline variables for follow-up completers versus non-completers without small-cell disclosure. Sensitivity analyses will include: thresholds of two/four check-ins; a model omitting completed-check-in count; missing-category indicators for optional context covariates; and, if assumptions and sample size allow, multiple imputation excluding the outcome from imputation claims. No missing desire/share response counts as “no.”

## Leakage and sensitivity analyses

Keep the selected APA outcome questionnaire in a separate form. The overlap audit identifies anticipated judgment and general sharing comfort as conceptually adjacent to outcome items. Refit the incremental model without those features and run the broader exclusions defined in the audit. Only check-ins timestamped before follow-up are permitted. Split or cross-validate by participant, never by check-in.

## Sample size

No confirmatory sample size is asserted yet. Before recruitment, specify the smallest effect of interest, expected attrition, expected undefined-gap rate, covariate count, target power, and calculation method. If the approved/recruited sample cannot support the model, label all inferential results exploratory and do not make a confirmatory claim.

## Reporting commitments

Report exclusions, attrition, feature coverage, all prespecified analyses, deviations, uncertainty, and null/negative results. Suppress small cells under the approved disclosure rule. Do not claim causation, diagnosis, treatment utility, population prevalence, or that privacy is unhealthy.

## Change control

Freeze and timestamp this document before viewing real outcomes. Amendments must identify the date, author, rationale, affected analyses, and whether they occurred before or after outcome access.
