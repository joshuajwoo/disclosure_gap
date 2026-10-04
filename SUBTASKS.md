# The Disclosure Gap — Subtask Breakdown

This file converts `PLAN.md` into implementation-sized tasks. The disclosure question is a personally meaningful case study; the portfolio contribution is the privacy-conscious, reproducible software system. Synthetic validation is the default path. Tasks related to real participants are optional and remain behind explicit institutional and security gates.

Tasks are ordered broadly by dependency; items marked **gate** must be completed before the dependent work begins. A task is not complete merely because documentation exists—the stated behavior must be demonstrable where implementation is involved.

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

## 1. Case-study framing, ethics, and measurement

- [x] **PRO-01 — Write the optional analysis-protocol draft**
  - Specify the exploratory question, outcome, primary feature, covariates, exclusion rules, missing-data approach, minimum completed check-ins, and analysis plan for a possible approved real study.
  - Done when every planned analysis maps to a prespecified question or is labeled exploratory. The draft is not evidence that recruitment is approved or required for the portfolio project.
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
- [ ] **PRO-10 — Align project-facing documents with the engineering case study**
  - Update the README, protocol introduction, limitations, and optional analysis protocol so they distinguish personal motivation, synthetic pipeline validation, and optional empirical research.
  - Add the existing related literature, sparse repeated measures, and the engineering-first positioning established in `PLAN.md`.
  - Done when no public-facing document frames the project as discovering a new psychological relationship or treats a synthetic result as a finding.

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
- [ ] **DAT-07 — Prove contract and schema evolution**
  - Add a second fixture contract or instrument version and document its compatible and incompatible changes.
  - Verify that migrations, API validation, exports, and the feature pipeline preserve version identity and do not silently reinterpret older records.
  - Done when CI exercises both versions and produces explicit failures for unsupported mappings.

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
  - Require a manual, authorized workflow; remove direct/operational identifiers; record export version, schema fingerprint, creation metadata, and provenance in an export audit record.
- [ ] **SEC-08 — Complete a pre-deployment security review — gate for real data**
  - Verify HTTPS, encryption at rest where supported, access control, dependency/security checks, logging safety, and export restrictions.

## 4. Synthetic data and fixtures

- [ ] **SYN-01 — Define synthetic participant scenarios**
  - Cover complete participation, partial completion, no desire to share, sharing after intent, choosing privacy, prefer-not-to-answer, varied audiences, and withdrawal.
  - Define cohort-level null, weak-effect, known-effect, and confounded scenarios. Parameters must describe the data-generating assumptions without implying that they represent real people.
- [ ] **SYN-02 — Implement the synthetic-data generator**
  - Generate contract-valid participants, assessments, four weeks of check-ins, and expected feature outputs using explicit parameters and a reproducible seed.
  - Support missingness, attrition, sparse denominators, and multiple supported contract versions.
- [ ] **SYN-03 — Add edge-case fixtures**
  - Include missing weeks, zero and one-event eligible denominators, duplicate attempts, invalid windows, sparse audience observations, extreme instrument values, withdrawal, and unsupported schema versions.
- [ ] **SYN-04 — Validate synthetic data**
  - Run contract checks, relational integrity checks, parameter/range checks, and a clear synthetic-data marker.
  - Verify that empirical feature summaries agree with expected behavior for seeded null, effect, missingness, and attrition scenarios within documented tolerances.
- [ ] **SYN-05 — Prevent synthetic/real data mixing**
  - Separate environments and configuration, and add safeguards so real records cannot be bundled into the frontend or committed.
- [ ] **SYN-06 — Add deterministic regression fixtures**
  - Commit small, reviewable synthetic fixtures with expected intermediate tables, feature values, exclusions, and report summaries.
  - Done when unintended pipeline changes fail tests with a useful explanation rather than silently changing published artifacts.

## 5. API implementation

- [ ] **API-01 — Bootstrap the FastAPI service**
  - Add configuration, database sessions, health checks, structured safe errors, and API versioning.
- [ ] **API-02 — Implement `POST /v1/participants`**
  - Validate age eligibility and consent version, create a random participant ID, record the consent event, and return an opaque session.
- [ ] **API-03 — Implement `POST /v1/assessments`**
  - Accept baseline or follow-up responses only during allowed windows and handle retries idempotently while rejecting conflicting duplicate submissions.
- [ ] **API-04 — Implement `POST /v1/check-ins`**
  - Validate structured responses, contract versions, week/window constraints, and idempotency keys while preserving all missing-value categories.
- [ ] **API-05 — Implement `GET /v1/me/trends`**
  - Return only neutral, descriptive summaries for the current participant.
  - Do not return diagnoses, risk predictions, cohort comparisons, or treatment guidance.
- [ ] **API-06 — Implement `DELETE /v1/me`**
  - Record withdrawal and delete or schedule deletion according to the consent and retention policy.
- [ ] **API-07 — Add API audit events**
  - Record only the minimal operational events needed to investigate failed submissions and deletion requests.
- [ ] **API-08 — Add API tests**
  - Test authorization, isolation, validation, safe retries, conflicting duplicates, versions, windows, withdrawal, deletion, redacted logging, and concurrency-sensitive constraints.

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
  - Present the project as an engineering case study, not as evidence that the case-study hypothesis is true.
- [ ] **WEB-10 — Complete accessibility checks**
  - Verify keyboard navigation, focus order, labels, error association, contrast, responsive layout, and screen-reader behavior for critical flows.
- [ ] **WEB-11 — Add critical user-flow tests**
  - Cover consent through follow-up, return sessions, validation errors, trends, withdrawal, deletion, and demo isolation in Playwright.

## 7. Research export and feature pipeline

- [ ] **RES-01 — Define the export schema**
  - Include only analysis-required fields plus schema, survey, and export versions; exclude session/recovery credentials and operational identifiers.
- [ ] **RES-02 — Implement the de-identified export**
  - Produce a versioned Parquet or equivalent research artifact through the restricted workflow and record its schema fingerprint and provenance.
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
  - Report coverage, distributions, denominator sizes, missingness, stability, minimum-check-in exclusions, feature-contract versions, and unsupported mappings.

## 8. Pipeline validation, exploratory analysis, and reporting

- [ ] **ANA-01 — Validate known synthetic scenarios**
  - Run null, weak-effect, known-effect, confounded, missingness, and attrition cohorts through the complete pipeline.
  - Compare generated summaries and estimates with scenario expectations using documented tolerances.
  - Done when the validation demonstrates pipeline behavior, without presenting synthetic estimates as research findings.
- [ ] **ANA-02 — Generate descriptive quality statistics**
  - Report cohort flow, completion, attrition, missingness, feature coverage, denominator sizes, and relationship-specific availability.
  - Make insufficient-data states visible instead of coercing them to zero.
- [ ] **ANA-03 — Implement the optional exploratory regression**
  - For an approved real dataset, regress follow-up social-anxiety score on the intention–action gap, baseline score, and a small set of prespecified context variables.
  - Report coefficient/effect size and uncertainty interval, not only a p-value, and state when the sample cannot answer the question.
  - The implementation may be exercised on synthetic data, but synthetic output is only a software test.
- [ ] **ANA-04 — Run the leakage sensitivity analysis**
  - Remove flagged predictor questions/features and report how estimates change; do not describe construct overlap as predictive success.
- [ ] **ANA-05 — Run missingness and attrition analyses**
  - Test prespecified missing-data assumptions and, for real data, compare included versus excluded or attrited participants where disclosure risk permits.
- [ ] **ANA-06 — Run feature-stability and robustness checks**
  - Assess sensitivity to sparse denominators, the minimum check-in threshold, influential observations, model specification, and feature-contract versions.
- [ ] **ANA-07 — Gate predictive modeling behind sample justification**
  - Keep prediction out of the core portfolio scope unless a documented sample-size and use-case review justifies it.
  - If prediction is later performed, keep all records from a participant in the same fold and evaluate uncertainty and calibration without making clinical claims.
- [ ] **ANA-08 — Perform privacy-safe subgroup checks only if justified**
  - For approved real data, analyze demographic groups only when both analytical power and disclosure thresholds are met; otherwise omit the comparison and explain why.
- [ ] **ANA-09 — Build aggregate figures and tables**
  - Create reproducible Altair or matplotlib outputs with clear labels, data-source markers, uncertainty, sample sizes, and no individual-level disclosure.
  - Apply an unmistakable synthetic label to every demo artifact generated from synthetic cohorts.
- [ ] **ANA-10 — Generate the reproducible report**
  - Separate pipeline validation from optional exploratory findings, state limitations, and report negative or uninformative results plainly.
  - Lead with the engineering purpose and never imply that a seeded synthetic association is an empirical discovery.
- [ ] **ANA-11 — Add a one-command rebuild**
  - Recreate validated intermediate tables, features, figures, and the report from a clean environment and explicit input version.

## 9. Validation, documentation, and readiness

- [ ] **VAL-01 — Conduct internal usability testing with synthetic data**
  - Verify question interpretation, sensitive wording, completion time, recovery, trends, withdrawal, and deletion.
- [ ] **VAL-02 — Revise confusing questions and version changes**
  - Record what changed, why, and whether contracts, fixtures, preregistration, or analysis code must also change.
- [ ] **VAL-03 — Validate the full vertical slice**
  - Run eligibility, consent, baseline, four check-ins, follow-up, trends, restricted export, synthetic validation, report generation, and deletion end to end.
- [ ] **VAL-04 — Test a fresh-environment reproduction**
  - From a clean checkout, start the stack, apply migrations, generate synthetic data, run tests, and rebuild the report.
- [ ] **VAL-05 — Write operational documentation**
  - Document deployment, rollback, migrations, backups, restore testing, incidents, access review, exports, and deletion requests.
- [ ] **VAL-06 — Write the system and case-study card**
  - Document the personal motivation, primary engineering contribution, intended use, non-uses, data source, contract versions, features, validation, privacy, ethics, and known failure modes.
  - Distinguish synthetic pipeline evidence from any empirical evidence and state that the system is not diagnostic or therapeutic.
- [ ] **VAL-07 — Complete the real-data readiness review — gate**
  - Confirm institutional approval, consent version, instrument permissions, threat model, security review, retention policy, access controls, and incident procedures.

## 10. Portfolio release and optional pilot

- [ ] **REL-01 — Deploy the synthetic demo**
  - Deploy the public web/API experience with synthetic data, HTTPS, monitoring, and environment isolation.
- [ ] **REL-02 — Verify the public artifact**
  - Confirm no real records, credentials, internal endpoints, small-cell results, or sensitive logs are exposed.
- [ ] **REL-03 — Publish the engineering case study**
  - Explain the personal motivation without claiming novelty, then document the architecture, versioned contracts, privacy lifecycle, synthetic scenarios, reproducibility evidence, tradeoffs, and limitations.
  - Describe the disclosure question as the system’s case study and explain why privacy choices are not pathology.
- [ ] **REL-04 — Run an approved adult usability pilot — optional**
  - Begin only after `PRO-07`, `SEC-08`, and `VAL-07` are cleared.
  - Track recruitment, consent, comprehension, technical failures, completion, and withdrawal without expanding data collection ad hoc.
- [ ] **REL-05 — Incorporate optional pilot feedback**
  - Version questionnaire and product changes and assess whether they require protocol or analysis-plan amendments.
- [ ] **REL-06 — Publish optional exploratory findings with appropriate claims**
  - Publish only after the relevant approval and adequacy review.
  - Label results exploratory unless a stronger design was approved, report uncertainty and negative or uninformative results, and avoid causal, diagnostic, clinical, novelty, or population-wide claims.

## Milestone mapping

| Milestone in `PLAN.md`             | Subtasks                                   | Completion check                                                                                                 |
| ---------------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| 1. Contracts and synthetic cohorts | FND-01–06, PRO-01–10, DAT-01–07, SYN-01–06 | Seeded null, effect, missingness, attrition, and schema-change scenarios pass versioned contract validation.     |
| 2. Tested vertical slice           | API-01–08, WEB-01–11                       | The complete participant flow passes API, browser, retry, duplicate, and accessibility tests.                    |
| 3. Privacy lifecycle               | SEC-01–07, API-06–08, WEB-07–08            | Isolation, recovery, restricted export, safe logging, withdrawal, and deletion behavior are verified.            |
| 4. Reproducible pipeline           | RES-01–08, ANA-01–11                       | One command rebuilds validated intermediates and a clearly labeled report from explicit, versioned inputs.       |
| 5. Portfolio release               | VAL-01–06, REL-01–03                       | The synthetic demo and engineering case study are public, reproducible, and make no unsupported research claims. |
| 6. Optional pilot                  | PRO-07, SEC-08, VAL-07, REL-04–06          | Any real-participant work has passed every institutional, security, analytical, and reporting gate.              |

## Critical dependency path

1. Freeze versioned questions, consent-for-testing, the data dictionary, and feature definitions (`PRO-02`–`PRO-09`, `DAT-01`–`DAT-02`).
2. Prove schema evolution and build deterministic synthetic scenarios (`DAT-03`–`DAT-07`, `SYN-01`–`SYN-06`).
3. Implement the tested participant vertical slice and core privacy controls (`SEC-01`–`SEC-06`, `API-01`–`API-08`, `WEB-01`–`WEB-11`).
4. Build the restricted export, feature, and synthetic-validation pipeline (`SEC-07`, `RES-01`–`RES-08`, `ANA-01`–`ANA-11`).
5. Complete clean-environment reproduction and publish the synthetic engineering case study (`VAL-01`–`VAL-06`, `REL-01`–`REL-03`).
6. Treat real-participant work as a separate optional path: clear institutional, security, and readiness gates before recruitment (`PRO-07`, `SEC-08`, `VAL-07`, `REL-04`–`REL-06`).
