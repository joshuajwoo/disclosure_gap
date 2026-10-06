# Engineering the Disclosure Gap

I started this project with a question that matters to me: what happens in the distance between wanting support and choosing not to ask for it? I do not treat that question as a new psychological discovery. Social anxiety, avoidance, disclosure, and help-seeking already have deep research literatures, and choosing privacy can be healthy. I used the question because it creates a demanding software problem.

The result is a longitudinal platform designed around boundaries that ordinary portfolio forms often skip. A participant can join without giving a name or email, receive opaque recovery credentials, complete versioned baseline and weekly forms, see only a neutral summary of their own fictional history, and delete the session. The API—not the browser—enforces windows, lifecycle order, exact versions, participant isolation, and idempotent retries.

The data pipeline is equally deliberate. A restricted export has no HTTP endpoint. It requires an authorized role and approval ID, excludes operational identifiers and exact timestamps, substitutes new analysis IDs, records provenance, and validates its own schema fingerprint and artifact digest. ETL rejects unknown mappings. Feature functions preserve missing states and use only observations before follow-up.

I built synthetic scenarios before treating analysis as an outcome. Null, weak-effect, known-effect, confounded, missingness, and attrition cohorts all travel through the same export, feature, quality, regression, figure, and report code. The generated associations are expected consequences of those assumptions. They demonstrate that the pipeline responds coherently; they say nothing about real people.

That distinction shapes the presentation. The public walkthrough is unmistakably synthetic and cannot contact the research API. It does not show diagnoses, risk scores, cohort comparisons, or recommendations. The outcome form remains separate from contextual predictors. Non-sharing states distinguish deliberate privacy, lack of a safe opportunity, lack of desire, uncertainty, and nonresponse.

The most useful engineering evidence is behavior: migrations apply to an empty database; duplicate and conflicting retries differ; one participant cannot read another; deletion revokes recovery; prohibited export fields and temporal leakage fail tests; version changes cannot silently fall forward; keyboard and Axe checks cover the critical browser flow; and `make report` rebuilds labeled artifacts from explicit inputs.

The tradeoffs are visible. Contact-free recovery is private but unforgiving when a code is lost. Four observations keep burden low but make denominators sparse. Strict versioning adds code but prevents silent reinterpretation. Avoiding free text minimizes risk but limits nuance. A small future convenience sample could test usability or support an exploratory association, but it would not justify causal, clinical, predictive, or population-wide claims.

The project succeeds as a software case study even if no real participant is ever recruited. Any optional pilot is a separate decision requiring institutional determination, approved consent, production security evidence, incident and backup readiness, and an adequacy review. Until those gates are cleared, the honest artifact is the synthetic system itself.
