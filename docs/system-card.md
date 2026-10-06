# System and case-study card

## Summary

The Disclosure Gap is a privacy-first longitudinal software case study motivated by a personal question: how can software represent moments when someone wants support but decides not to ask for it? Its primary contribution is the engineering system, not a new psychological claim.

## Intended use

- demonstrate versioned longitudinal collection and schema evolution;
- exercise consent, recovery, withdrawal, and deletion as product workflows;
- validate de-identified export, feature, analysis, and reporting code on deterministic synthetic cohorts;
- support a separately approved, limited exploratory adult study only if every institutional and security gate is later cleared.

## Non-uses

The system is not diagnostic, therapeutic, a crisis service, a clinical screener, a tool for inferring undisclosed feelings, evidence that privacy is unhealthy, or a basis for individual decisions. Synthetic output is not empirical evidence. It must not be used with minors under the current protocol.

## Data and versions

The public path uses generated records marked synthetic. Contracts `1.0.0-draft` and the CI-only additive fixture `1.1.0-fixture` are mapped explicitly; unknown versions fail. Consent `0.2.0` is approved only for synthetic/developer testing. The outcome identity is APA DSM-5-TR Severity Measure for Social Anxiety Disorder—Adult, version `DSM-5-TR-2022`; the public application links official wording rather than maintaining a copy.

## Features

Feature contract `1.0.0-draft` defines the intention–action gap, audience asymmetry, topic sensitivity gap, anticipated-judgment rate, support-mismatch rate, and within-person comfort variability. Features use only check-ins preceding follow-up. Sparse or ineligible denominators become explicit missing values, never zeros.

## Privacy and security

The application does not request names, contacts, exact locations, social accounts, or disclosure text. Participant identifiers and credentials are random; only strong recovery hashes and session-token hashes are stored. Participant authorization is token-scoped. Logs use a narrow event allowlist. Deletion removes response records and credentials. Restricted exports use new analysis IDs, relative study days, allowlisted fields, fingerprints, digests, and audit provenance, with no public endpoint.

## Validation evidence

- exact JSON Schema and typed API validation;
- migration and relational-integrity tests;
- authentication, isolation, idempotency, window, logging, recovery, and deletion tests;
- browser flows for eligibility through follow-up, recovery, trends, and deletion;
- keyboard, focus, mobile-overflow, and Axe accessibility checks;
- deterministic null, weak-effect, known-effect, confounded, missingness, attrition, edge, and version-change fixtures;
- tamper, orphan, duplicate, invalid-value, and temporal export rejection;
- one-command labeled synthetic report reproduction.

## Analysis boundary

Synthetic regressions test code behavior only. The optional real-data path reports associations with uncertainty and keeps leakage-sensitive predictors in a separate sensitivity model. Prediction is gated behind sample and use-case justification. Subgroups are omitted without both analytical adequacy and disclosure-safe cell sizes.

## Ethical boundary

Lower disclosure may represent preference, culture, safety, autonomy, or a healthy boundary. The software therefore preserves `chose_private`, no safe opportunity, no desire to share, not applicable, and prefer not to answer as different states. It does not rank those choices morally or clinically.

## Known failure modes and limitations

- Four weekly observations produce sparse denominators and unstable relationship-specific features.
- Self-report does not establish what happened outside the form.
- Convenience samples would limit generalization and causal interpretation.
- Recovery codes cannot be emailed or looked up because contact data are intentionally absent.
- Deleting credentials makes a lost session unrecoverable.
- A compromised browser or hosting account can defeat application-level protections.
- Synthetic scenarios reflect authored assumptions and can miss real-world behavior.
- Accessibility automation does not replace testing with disabled users.
- Real-data security, incident response, backups, institutional review, and deployment controls remain unverified.

## Current readiness

Synthetic local development and portfolio demonstration are supported. Real recruitment is not approved. The unresolved items in the readiness review and pre-deployment security review are hard gates, not future cleanup suggestions.
