# Pre-deployment security review

Review date: 2026-10-04. Outcome: **synthetic local development may continue; real-data deployment gate is closed**.

| Control                          | Evidence / status                                                                                                                    |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Data minimization                | Structured contracts exclude direct identity, free text, contacts, locations, and social accounts.                                   |
| Authentication at rest           | Session tokens use SHA-256 hashes; recovery codes use salted scrypt hashes. Plain values are returned once.                          |
| Participant isolation            | Self routes derive scope from the bearer-token hash and never accept a participant ID. API tests exercise cross-participant denial.  |
| Consent, withdrawal, deletion    | Versioned consent is persisted; deletion removes response rows and credentials and leaves a minimal inaccessible tombstone.          |
| Validation/integrity             | Exact versions, server-side windows, idempotency payload hashes, and database uniqueness constraints are tested.                     |
| Logging                          | Application logs omit bodies, headers, tokens, participant IDs, and response content; audit fields are allowlisted.                  |
| Environment separation           | Synthetic defaults, double real-data gate, ignored data/export directories, and synthetic-marker checks are in place.                |
| Dependency integrity             | Node/Python versions and dependency files are pinned; lint, type, unit, migration, and browser safety checks run in CI.              |
| Restricted exports               | Manual role and audit design is documented; no public export endpoint exists. Implementation remains phase 7.                        |
| HTTPS and encryption at rest     | Required for production but not configured or evidenced by this local Compose stack. **Blocker.**                                    |
| Rate limiting / abuse monitoring | Required for enrollment, authentication, and recovery before real use. **Blocker.**                                                  |
| Deployment IAM and secret store  | Requirements are documented but no production environment is in scope. **Blocker.**                                                  |
| Backup/restore/deletion replay   | Policy requirements exist; provider-specific evidence and restore test are absent. **Blocker.**                                      |
| Automated vulnerability scanning | Lockfiles exist; a production process for continuous Node, Python, image, and deployment scanning is not yet evidenced. **Blocker.** |
| Institutional/readiness gates    | `PRO-07` and `VAL-07` are not cleared. **Blocker.**                                                                                  |

This completed review records an explicit negative gate decision. `SEC-08` must be reviewed again—and the blockers closed—before enabling real-participant configuration.
