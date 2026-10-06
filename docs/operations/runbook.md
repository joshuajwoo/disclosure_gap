# Operations runbook

This runbook supports the synthetic portfolio environment. It does not authorize real-participant collection.

## Deployment prerequisites

An operator must select a hosting provider and supply its account/project credentials. The public release must use a separate project, database, network, and secret namespace from any future research environment. Required release configuration is:

- `APP_ENV=public-demo`
- `ALLOW_REAL_PARTICIPANT_DATA=false`
- `REAL_DATA_READINESS_APPROVED=false`
- `NEXT_PUBLIC_DEMO_MODE=true`
- an HTTPS public origin in `WEB_ORIGIN`
- no database or API URL embedded in the public web build unless a separately reviewed synthetic API is intentionally deployed

Terminate TLS at the hosting platform or reverse proxy, redirect HTTP to HTTPS, enable platform health monitoring, and retain only availability and safe structured operational logs. Do not send response bodies, authorization headers, recovery codes, URLs with tokens, or export contents to monitoring services.

## Release and rollback

1. Build immutable images from a reviewed commit and record the commit digest.
2. Apply migrations with the migrator role before shifting traffic.
3. Verify `/health`, the synthetic banner, demo isolation, response headers, and deletion behavior.
4. Retain the previous known-good image digest.
5. For an application regression, route traffic back to the previous image. Do not automatically downgrade the database.
6. If a migration is implicated, stop writes and use a reviewed forward repair. Restore from backup only after impact and data-loss review.

## Migrations

Use the schema-migrator credential only for `alembic upgrade head`; the runtime API role must not own or create schema objects. Test each migration on an empty database and a disposable copy of the prior schema. Record start/end time, revision, operator, and outcome. Never edit an applied revision in place.

## Backups and restore testing

The public synthetic demo does not require durable participant records. If a database is nevertheless deployed, encrypt backups, restrict them to the operations role, and apply the same synthetic-only boundary. A future approved research environment needs a documented recovery-point objective, recovery-time objective, retention period, deletion treatment, and quarterly restore test before launch. A restore test must verify row counts, constraints, application health, and deletion tombstones in an isolated environment.

## Monitoring and incidents

Monitor uptime, health-check failures, server error counts, migration failures, storage pressure, and dependency/security alerts. Use only the event allowlist in the logging policy. For a suspected exposure:

1. restrict access and preserve safe operational evidence;
2. rotate affected credentials and invalidate sessions;
3. identify environment, time window, and data classes without copying sensitive records into tickets;
4. notify the project owner and applicable institutional/security contacts;
5. document containment, eradication, recovery, and corrective actions;
6. do not resume real-data collection without formal approval.

## Access review

Review hosting administrators, database roles, secret access, CI deploy identities, backup access, and export authorization at least quarterly and whenever a collaborator leaves. Remove unused access immediately. The `research_exporter` role must be separate from ordinary application administration and every export requires an approval identifier.

## Restricted exports

There is no export HTTP route. An authorized operator invokes `research.export.create_restricted_export` from a least-privilege session, records the approval ID, validates the resulting fingerprint and artifact digest, and transfers it only to approved restricted storage. Deleted participants, credentials, operational identifiers, payload hashes, exact timestamps, and direct identifiers are excluded.

## Deletion requests

Participant deletion invalidates session and recovery credentials, removes response tables, and retains only the documented tombstone/audit state. Confirm that authenticated access and recovery fail afterward. If an approved derived export exists, follow `docs/security/retention-and-deletion.md`; do not claim immediate deletion from immutable backups where the policy specifies expiry instead.
