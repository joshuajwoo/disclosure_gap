# The Disclosure Gap — Subtask Breakdown

This file converts `PLAN.md` into implementation-sized tasks. Tasks are ordered by dependency; items marked **gate** must be completed before the dependent work begins.

## 0. Project foundations

- [x] **FND-01 — Create the repository structure**
  - Add `apps/web`, `apps/api`, `packages/contracts`, `research`, `infra`, `docs`, and `tests`.
  - Done when each area has a short README describing its ownership and purpose.
- [x] **FND-02 — Define local development commands**
  - Establish commands for setup, development, linting, testing, migrations, synthetic-data generation, and report generation.
  - Done when a new contributor can discover all commands from the root README.
- [x] **FND-03 — Pin the initial toolchain and dependencies**
  - Pin Node, Python, package-manager, application, analysis, lint, and test versions.
  - Done when dependency installation is reproducible from lockfiles.
- [x] **FND-04 — Configure quality checks**
  - Configure Ruff, ESLint, pytest, Playwright, and type checking for Python and TypeScript.
  - Done when one local command runs all static checks and tests.
- [x] **FND-05 — Add continuous integration**
  - Run install, lint, type checks, unit tests, migration checks, and critical-flow tests in GitHub Actions.
  - Done when CI runs on pull requests and the default branch.
- [x] **FND-06 — Configure the local stack**
  - Add Docker Compose services for the web app, API, and PostgreSQL.
  - Provide example environment variables containing no real credentials.
  - Done when the stack starts from a clean checkout using documented commands.
  - Verified: all three services started, PostgreSQL became healthy, migration `0001` applied, and the temporary stack stopped cleanly on 2026-10-04.

## 1. Protocol, ethics, and measurement

- [x] **PRO-01 — Write the preregistration draft**
  - Specify the research question, primary hypothesis, outcome, predictor, covariates, exclusion rules, missing-data approach, minimum completed check-ins, and analysis plan.
  - Done when every planned analysis maps to a prespecified question or is labeled exploratory.
- [x] **PRO-02 — Resolve the social-anxiety instrument — gate**
  - Confirm permitted use, scoring, suitability for ages 18–22, and suitability for repeated baseline/follow-up measurement.
  - If an initial candidate is unsuitable, document and select an alternative before building assessment forms.
  - Done when the decision, version, citation, license/permission status, and scoring rules are recorded.
  - Resolution: selected the APA DSM-5-TR Severity Measure for Social Anxiety Disorder—Adult; researcher reproduction, adult use, repeated administration, scoring, and version are documented.
- [x] **PRO-03 — Draft the exact survey questions**
  - Draft eligibility, baseline context, perceived support, sharing comfort, weekly check-in, and follow-up questions.
  - Include “not applicable,” “prefer not to answer,” and “I chose to keep it private” where relevant.
  - Exclude names, contacts, exact locations, social accounts, and free-text disclosure content.
  - Resolution: original questions are fixed in `survey.md`; outcome wording and order are fixed by the official APA normative PDF and `SAD01`–`SAD10` contract.
- [x] **PRO-04 — Audit predictor/outcome overlap**
  - Map each predictor question against every outcome item and flag possible rewording or construct leakage.
  - Done when the sensitivity-analysis exclusion set is defined.
  - Resolution: all predictor fields are mapped to the selected outcome’s ten item domains with prespecified leakage exclusions and sensitivity models.
- [x] **PRO-05 — Define neutral participant language**
  - Review consent, prompts, validation errors, trends, withdrawal, and completion text.
  - Ensure the product does not diagnose, score privacy choices, predict individual risk, or offer treatment advice.
- [x] **PRO-06 — Write consent and withdrawal materials — gate**
  - Cover purpose, procedures, risks, voluntary participation, data handling, retention, withdrawal/deletion, and contacts required by the applicable review process.
  - Done when consent is versioned and approved for synthetic/internal testing.
  - Resolution: consent version 0.2.0 is approved for synthetic/developer testing only. Real recruitment still requires institution-specific completion and PRO-07 clearance.
- [x] **PRO-07 — Determine institutional review requirements — gate for real recruitment**
  - Document whether IRB or another institutional process applies and what approval is required.
  - Do not recruit real participants until this gate is cleared.
  - Status: treat as human-subjects research and obtain a formal institutional determination; the recruitment gate is not cleared.
- [x] **PRO-08 — Write the data dictionary**
  - Define every field, type, allowed value, missing-value meaning, source question, sensitivity, and retention rule.
  - Keep “prefer not to answer,” “not applicable,” and true zero values distinct.
- [x] **PRO-09 — Write the research limitations statement**
  - Cover healthy privacy, boundaries, unsafe relationships, culture, convenience sampling, association versus causation, and the separate requirements for minors.

## 2. Contracts and data design

- [x] **DAT-01 — Version the survey contract**
  - Define versioned schemas for eligibility, consent, assessments, check-ins, and participant trend summaries.
  - Done when frontend and API can generate or validate payloads from the same documented contract.
- [x] **DAT-02 — Define feature contracts**
  - Specify inputs, formulas, eligible rows, denominators, missingness behavior, and output types for every engineered feature.
  - Include the intention–action gap, audience asymmetry, topic sensitivity gap, anticipated judgment rate, support mismatch, and within-person variability.
- [x] **DAT-03 — Design the relational schema**
  - Model `participants`, `consent_events`, `assessments`, `check_ins`, and `study_events` with foreign keys and timestamps.
  - Ensure participant identifiers are random and contain no direct identity data.
- [x] **DAT-04 — Define lifecycle constraints**
  - Specify assessment windows, one submission per type/window, one check-in per participant/week, withdrawal states, and deletion behavior.
- [x] **DAT-05 — Create the initial database migration**
  - Implement the schema and integrity constraints in SQLAlchemy/Alembic.
  - Done when migrations apply to an empty database and can be tested in CI.
- [x] **DAT-06 — Document raw-to-feature lineage**
  - Create an auditable mapping from each raw question and response code to every derived variable.

## 3. Privacy and security

- [ ] **SEC-01 — Create a threat model**
  - Identify assets, actors, trust boundaries, abuse cases, re-identification risks, and mitigations for the browser, API, database, exports, and public demo.
- [ ] **SEC-02 — Minimize operational logging**
  - Define the limited `study_events` allowlist and prohibit sensitive response bodies, tokens, and disclosure content in logs.
- [ ] **SEC-03 — Implement participant authentication/recovery**
  - Use an opaque session and random recovery code or equivalent mechanism without requiring contact information.
  - Store only a strong hash of the recovery code.
- [ ] **SEC-04 — Enforce participant data isolation**
  - Ensure self-view, submission, withdrawal, and deletion operations can access only the authenticated participant’s records.
- [ ] **SEC-05 — Implement secrets and credential handling**
  - Keep secrets out of source control and use least-privilege database credentials and deployment secret stores.
- [ ] **SEC-06 — Write the retention and deletion policy**
  - Define retention periods, withdrawal semantics, backups, derived exports, and deletion verification.
- [ ] **SEC-07 — Design restricted research exports**
  - Require a manual, authorized workflow; remove direct/operational identifiers; record export version and provenance.
- [ ] **SEC-08 — Complete a pre-deployment security review — gate for real data**
  - Verify HTTPS, encryption at rest where supported, access control, dependency/security checks, logging safety, and export restrictions.

## 4. Synthetic data and fixtures

- [ ] **SYN-01 — Define synthetic participant scenarios**
  - Cover complete participation, partial completion, no desire to share, sharing after intent, choosing privacy, prefer-not-to-answer, varied audiences, and withdrawal.
- [ ] **SYN-02 — Implement the synthetic-data generator**
  - Generate contract-valid participants, assessments, four weeks of check-ins, and expected feature outputs using a reproducible seed.
- [ ] **SYN-03 — Add edge-case fixtures**
  - Include missing weeks, zero eligible denominators, duplicate attempts, invalid windows, sparse audience observations, and extreme instrument values.
- [ ] **SYN-04 — Validate synthetic data**
  - Run contract checks, relational integrity checks, realistic range checks, and a clear synthetic-data marker.
- [ ] **SYN-05 — Prevent synthetic/real data mixing**
  - Separate environments and configuration, and add safeguards so real records cannot be bundled into the frontend or committed.

## 5. API implementation

- [ ] **API-01 — Bootstrap the FastAPI service**
  - Add configuration, database sessions, health checks, structured safe errors, and API versioning.
- [ ] **API-02 — Implement `POST /v1/participants`**
  - Validate age eligibility and consent version, create a random participant ID, record the consent event, and return an opaque session.
- [ ] **API-03 — Implement `POST /v1/assessments`**
  - Accept baseline or follow-up responses only during allowed windows and reject invalid or duplicate submissions.
- [ ] **API-04 — Implement `POST /v1/check-ins`**
  - Validate structured responses, week/window constraints, and duplicate submissions while preserving all missing-value categories.
- [ ] **API-05 — Implement `GET /v1/me/trends`**
  - Return only neutral, descriptive summaries for the current participant.
  - Do not return diagnoses, risk predictions, cohort comparisons, or treatment guidance.
- [ ] **API-06 — Implement `DELETE /v1/me`**
  - Record withdrawal and delete or schedule deletion according to the consent and retention policy.
- [ ] **API-07 — Add API audit events**
  - Record only the minimal operational events needed to investigate failed submissions and deletion requests.
- [ ] **API-08 — Add API tests**
  - Test authorization, isolation, validation, duplicates, windows, withdrawal, deletion, redacted logging, and concurrency-sensitive constraints.

## 6. Participant web application

- [ ] **WEB-01 — Bootstrap the Next.js application**
  - Configure TypeScript, Tailwind CSS, API access, error handling, and accessible shared components.
- [ ] **WEB-02 — Build eligibility and consent flow**
  - Show versioned consent, confirm ages 18–22, handle ineligibility neutrally, and create the participant session.
- [ ] **WEB-03 — Build baseline assessment flow**
  - Render the chosen instrument separately from predictor/context questions and preserve partial/missing response semantics.
- [ ] **WEB-04 — Build weekly check-in flow**
  - Collect desire to share, intended audience, action, comfort, anticipated judgment, support confidence, and explicit privacy/nonresponse choices.
- [ ] **WEB-05 — Build follow-up assessment flow**
  - Reuse the versioned outcome instrument and enforce the follow-up window.
- [ ] **WEB-06 — Build participant trends**
  - Present only the participant’s descriptive history with neutral explanations and appropriate sparse-data states.
- [ ] **WEB-07 — Build return/recovery flow**
  - Allow participants to resume without providing contact information and explain how to protect the recovery code.
- [ ] **WEB-08 — Build withdrawal/deletion flow**
  - Clearly describe consequences, require confirmation, call the deletion endpoint, and terminate the session.
- [ ] **WEB-09 — Build synthetic public-demo mode**
  - Use synthetic records only, label them clearly, and prevent demo actions from reaching the research environment.
- [ ] **WEB-10 — Complete accessibility checks**
  - Verify keyboard navigation, focus order, labels, error association, contrast, responsive layout, and screen-reader behavior for critical flows.
- [ ] **WEB-11 — Add critical user-flow tests**
  - Cover consent through follow-up, return sessions, validation errors, trends, withdrawal, deletion, and demo isolation in Playwright.

## 7. Research export and feature pipeline

- [ ] **RES-01 — Define the export schema**
  - Include only analysis-required fields plus schema, survey, and export versions; exclude session/recovery credentials and operational identifiers.
- [ ] **RES-02 — Implement the de-identified export**
  - Produce a versioned Parquet or equivalent research artifact through the restricted workflow.
- [ ] **RES-03 — Implement export validation**
  - Check uniqueness, joins, allowed values, date ordering, withdrawal handling, and absence of prohibited fields.
- [ ] **RES-04 — Build reproducible ETL**
  - Load raw exports, validate versions, normalize response codes, preserve missingness, and create analysis-ready tables.
- [ ] **RES-05 — Implement the intention–action gap**
  - Use only pre-follow-up check-ins and the preregistered minimum-completion rule.
  - Return missing—not zero—when there are no eligible `wanted_to_share = true` weeks.
- [ ] **RES-06 — Implement secondary features**
  - Add audience asymmetry, topic sensitivity gap, anticipated judgment rate, support mismatch, and within-person variability exactly as contracted.
- [ ] **RES-07 — Add feature unit tests**
  - Test formulas, eligible denominators, sparse observations, missing categories, time cutoffs, and expected values from synthetic fixtures.
- [ ] **RES-08 — Produce a feature-quality report**
  - Report coverage, distributions, denominator sizes, missingness, stability, and minimum-check-in exclusions.

## 8. Statistical analysis and reporting

- [ ] **ANA-01 — Generate descriptive statistics**
  - Report recruitment/flow counts, completion, attrition, missingness, feature distributions, and relationship-specific patterns.
- [ ] **ANA-02 — Implement the primary regression**
  - Regress follow-up social-anxiety score on the intention–action gap, baseline score, and prespecified context variables.
  - Report coefficient/effect size and uncertainty interval, not only a p-value.
- [ ] **ANA-03 — Compare incremental value**
  - Compare a baseline-only model with a model adding engineered features.
  - Keep all records from a participant in the same train/test or cross-validation fold.
- [ ] **ANA-04 — Run the leakage sensitivity analysis**
  - Remove flagged predictor questions/features and report how estimates and performance change.
- [ ] **ANA-05 — Run missingness and attrition analyses**
  - Test prespecified missing-data assumptions and compare included versus excluded/attrited participants where disclosure risk permits.
- [ ] **ANA-06 — Run feature-stability and robustness checks**
  - Assess sensitivity to the minimum check-in threshold, influential observations, model specification, and feature definitions.
- [ ] **ANA-07 — Evaluate optional predictive models only if justified**
  - Establish a sample-size criterion before adding regularized models.
  - If prediction is performed, evaluate uncertainty, calibration, and participant-level validation.
- [ ] **ANA-08 — Perform privacy-safe subgroup checks**
  - Analyze available demographic groups only when sample sizes meet the disclosure threshold; suppress small cells.
- [ ] **ANA-09 — Build aggregate figures and tables**
  - Create reproducible Altair or matplotlib outputs with clear labels, uncertainty, sample sizes, and no individual-level disclosure.
- [ ] **ANA-10 — Generate the reproducible report**
  - Label confirmatory versus exploratory analyses, state limitations, and report negative findings plainly.
- [ ] **ANA-11 — Add a one-command rebuild**
  - Recreate all analysis tables, figures, and the report from a validated input export in a fresh environment.

## 9. Validation, documentation, and readiness

- [ ] **VAL-01 — Conduct internal usability testing with synthetic data**
  - Verify question interpretation, sensitive wording, completion time, recovery, trends, withdrawal, and deletion.
- [ ] **VAL-02 — Revise confusing questions and version changes**
  - Record what changed, why, and whether contracts, fixtures, preregistration, or analysis code must also change.
- [ ] **VAL-03 — Validate the full vertical slice**
  - Run eligibility, consent, baseline, four check-ins, follow-up, trends, export, analysis, and deletion end to end.
- [ ] **VAL-04 — Test a fresh-environment reproduction**
  - From a clean checkout, start the stack, apply migrations, generate synthetic data, run tests, and rebuild the report.
- [ ] **VAL-05 — Write operational documentation**
  - Document deployment, rollback, migrations, backups, restore testing, incidents, access review, exports, and deletion requests.
- [ ] **VAL-06 — Write the model/research card**
  - Document intended use, non-uses, population limits, data source, features, evaluation, privacy, ethics, and known failure modes.
- [ ] **VAL-07 — Complete the real-data readiness review — gate**
  - Confirm institutional approval, consent version, instrument permissions, threat model, security review, retention policy, access controls, and incident procedures.

## 10. Pilot and portfolio release

- [ ] **REL-01 — Deploy the synthetic demo**
  - Deploy the public web/API experience with synthetic data, HTTPS, monitoring, and environment isolation.
- [ ] **REL-02 — Verify the public artifact**
  - Confirm no real records, credentials, internal endpoints, small-cell results, or sensitive logs are exposed.
- [ ] **REL-03 — Publish methods and limitations**
  - Explain the hypothesis, design, feature definitions, validation strategy, ethical constraints, and why privacy choices are not pathology.
- [ ] **REL-04 — Run an approved adult usability pilot**
  - Begin only after `PRO-07`, `SEC-08`, and `VAL-07` are cleared.
  - Track recruitment, consent, comprehension, technical failures, completion, and withdrawal without expanding data collection ad hoc.
- [ ] **REL-05 — Incorporate pilot feedback**
  - Version questionnaire and product changes and assess whether they require protocol or analysis-plan amendments.
- [ ] **REL-06 — Publish findings with appropriate claims**
  - State whether results are confirmatory or exploratory, report uncertainty and negative results, and avoid causal, diagnostic, clinical, or population-wide claims.

## Milestone mapping

| Milestone in `PLAN.md`    | Subtasks                                   | Completion check                                                                               |
| ------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| 1. Protocol and mock data | FND-01–06, PRO-01–09, DAT-01–06, SYN-01–05 | A synthetic participant can complete all study weeks under versioned contracts.                |
| 2. Vertical slice         | SEC-01–06, API-01–08, WEB-01–11            | The complete participant flow passes end-to-end and accessibility tests, including deletion.   |
| 3. Research pipeline      | SEC-07, RES-01–08, ANA-01–02, ANA-09–11    | One command rebuilds all tables and figures from a validated export.                           |
| 4. Validation             | ANA-03–08, ANA-10, VAL-01–06               | A clean environment reproduces a limitations-aware report with leakage and missingness checks. |
| 5. Pilot and portfolio    | PRO-07, SEC-08, VAL-07, REL-01–06          | The synthetic demo is public; any real pilot has passed all approval and security gates.       |

## Critical dependency path

1. Resolve the measurement instrument and review requirements (`PRO-02`, `PRO-07`).
2. Freeze versioned questions, consent, data dictionary, and feature definitions (`PRO-03`–`PRO-08`, `DAT-01`–`DAT-02`).
3. Implement schema, synthetic data, and privacy controls (`DAT-03`–`DAT-06`, `SEC-01`–`SEC-07`, `SYN-01`–`SYN-05`).
4. Build and test the participant vertical slice (`API-01`–`API-08`, `WEB-01`–`WEB-11`).
5. Build the export, feature, and analysis pipeline (`RES-01`–`RES-08`, `ANA-01`–`ANA-11`).
6. Complete reproducibility, security, and real-data readiness gates (`SEC-08`, `VAL-01`–`VAL-07`).
7. Release the synthetic portfolio first; conduct real recruitment only after all gates are cleared (`REL-01`–`REL-06`).
