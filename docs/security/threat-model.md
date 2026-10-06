# Threat model

Version 1.0.0, reviewed 2026-10-04. Scope: browser, API, PostgreSQL, restricted export workflow, synthetic generator, and public demo. Real-participant deployment remains prohibited.

## Assets and sensitivity

| Asset                                       | Primary concern                                                                               |
| ------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Structured assessment/check-in responses    | Sensitive mental-health-related and interpersonal information; confidentiality and integrity. |
| Participant session and recovery secrets    | Account access; confidentiality and revocation.                                               |
| Consent and withdrawal history              | Compliance integrity and availability.                                                        |
| Contract/instrument versions and timestamps | Correct interpretation, ordering, and reproducibility.                                        |
| Research exports                            | Re-identification through combinations, unauthorized copying, or provenance loss.             |
| Synthetic/public-demo records               | Integrity and unmistakable labeling; prevention of real-data mixing.                          |

Names, emails, phone numbers, contact lists, exact locations, social accounts, concern text, and message contents are outside the data model.

## Actors

- A participant using their own opaque session or recovery code.
- Another participant attempting horizontal access.
- A public visitor or automated attacker probing validation and authentication.
- An authorized developer/operator who may make a mistake or exceed their need-to-know access.
- An authorized analyst receiving a restricted, minimized export.
- A compromised browser, dependency, deployment secret, server, database credential, backup, or analyst workstation.

## Trust boundaries

1. Participant browser to HTTPS ingress/API. Browser state and client timestamps are untrusted.
2. API validation/authentication to application services. Only exact contract versions and authenticated participant scope cross this boundary.
3. API to PostgreSQL. Database constraints remain a final guard against duplicate or invalid state.
4. Database to the manual export process. There is no participant-facing or public export route.
5. Restricted export to analyst environment. Exported rows are minimized, versioned, fingerprinted, and auditable.
6. Synthetic generator to public demo and committed fixtures. Real-data configuration is forbidden on this path.

## Abuse cases and controls

| Abuse or failure                               | Controls                                                                                                                                             | Residual risk / required follow-up                                                                                  |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Guess or steal a participant session           | 256-bit random token, SHA-256 token hash at rest, HTTPS requirement, token rotation on recovery, invalidation on deletion.                           | Browser compromise can expose an active token; add deployment cookie/header policy and rate limits before real use. |
| Guess a recovery code                          | 80-bit random code, per-record scrypt salt/hash, participant ID required, generic failure response.                                                  | Add distributed rate limiting and monitoring before real use.                                                       |
| Access another participant’s records           | Server derives participant only from token hash; every query is scoped to that ID; no client-supplied participant ID on self routes.                 | Authorization regression remains possible; isolation tests are mandatory.                                           |
| Replay or race a submission                    | Required idempotency key, canonical payload hash, per-participant uniqueness constraints, conflict response.                                         | Database-specific concurrency tests are required before real use.                                                   |
| Bypass study timing                            | Server creation time and server receipt time define windows; client `completedAt` is never authoritative.                                            | Clock/configuration error; production time synchronization and alerting required.                                   |
| Inject unsupported semantics                   | Exact-version Pydantic/JSON Schema dispatch; unsupported versions fail before mapping; source versions persist.                                      | Every future version needs a reviewed mapping and migration decision.                                               |
| Leak answers into logs/errors                  | Structured allowlisted audit fields only; generic errors; request logger records method, path, status, and request ID, never bodies or auth headers. | Infrastructure/proxy logging must be reviewed separately.                                                           |
| Re-identify an export                          | No direct identifiers or credentials; minimize timestamps and fields; small-cell rules; manual role authorization; schema and artifact digests.      | Longitudinal patterns can still identify people; a disclosure review is required per export.                        |
| Mix real data into the public demo             | Synthetic-only environment names, two affirmative configuration gates for real data, ignored `data/` and `exports/`, synthetic marker validation.    | Deployment/IAM separation must be proven before real use.                                                           |
| Recover deleted responses from backups/exports | Tombstone live access immediately; delete response rows; track backup expiry and derived artifacts under the retention policy.                       | Immediate erasure from immutable backups may be impossible and must be disclosed.                                   |
| Malicious dependency or stolen secret          | Pinned lockfiles, secret-free example config, deployment secret-store requirement, least-privilege roles, dependency review.                         | Automated Python vulnerability scanning and production secret rotation remain pre-deployment items.                 |

## Re-identification assessment

The absence of names does not make longitudinal records anonymous. Age band, timestamps, rare response combinations, audience patterns, and small subgroups can be identifying together. Exports therefore use a separate analysis identifier, coarsen or omit operational timestamps, suppress small cells, and require a documented purpose and disclosure review. Public artifacts contain synthetic aggregates only.

## Review triggers

Repeat this review after adding a contract field, free text, demographic variable, authentication method, third-party service, deployment environment, export destination, or real-data protocol.
