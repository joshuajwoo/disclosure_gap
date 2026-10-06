# Real-data readiness review

**Review date:** 2026-10-04

**Decision:** **NOT READY — REAL-PARTICIPANT GATE CLOSED**

Completing this review records the decision; it does not approve recruitment. The synthetic portfolio system may continue. No real participant may be enrolled until every blocking item is evidenced and the review is repeated.

| Area                        | Evidence                                                                                                                     | Status                               |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Institutional determination | `docs/protocol/review-requirements.md` requires a formal determination. No determination identifier or approval is recorded. | Blocking                             |
| Consent                     | Version `0.2.0` is approved only for synthetic/developer testing. Institution-specific contacts and approval are absent.     | Blocking                             |
| Instrument                  | Adult instrument identity, scoring, normative source, and research reproduction are documented.                              | Ready for institutional confirmation |
| Population                  | Adults 18–22 only; minors are excluded.                                                                                      | Defined                              |
| Data minimization           | No direct contact, exact location, social account, or disclosure-content fields.                                             | Implemented                          |
| Threat model and logging    | Threat model, safe event allowlist, isolation, credential hashing, and automated redaction tests exist.                      | Implemented locally                  |
| Transport and storage       | No production HTTPS or encryption-at-rest evidence exists.                                                                   | Blocking                             |
| Hosting IAM and secrets     | No production project, least-privilege role evidence, secret store, or access-review record exists.                          | Blocking                             |
| Abuse protection            | Production rate limiting and operational alert thresholds are not implemented or evidenced.                                  | Blocking                             |
| Backups and restore         | Policy exists, but no approved-research backup configuration or successful restore-test record exists.                       | Blocking                             |
| Incident response           | Runbook exists, but institutional contacts, notification duties, and an exercised incident drill are absent.                 | Blocking                             |
| Retention and deletion      | Policy and application deletion behavior exist; backup/export deletion behavior is documented.                               | Requires production verification     |
| Restricted export           | Manual role/approval gate, de-identification, audit provenance, and validation tests exist.                                  | Implemented locally                  |
| Dependency scanning         | Pinned dependencies and CI checks exist; continuous production vulnerability monitoring is not evidenced.                    | Blocking                             |
| Analytical adequacy         | No approved recruitment target or achieved sample exists. Prediction and subgroup analyses remain gated.                     | Blocking                             |

## Conditions to reopen the gate

Provide the institutional determination, approved consent materials and contacts, production architecture and provider, HTTPS/encryption evidence, least-privilege IAM and secret configuration, rate-limit and monitoring evidence, backup/restore test, incident contacts and drill, dependency-scanning record, retention confirmation, and approved sample/analysis plan. Then repeat both this review and the pre-deployment security review with named reviewers and dated evidence.
