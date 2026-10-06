# Operations runbook

This runbook supports the synthetic portfolio environment. It does not authorize real-participant collection.

## Deployment prerequisites

The synthetic portfolio release uses GitHub Pages at `https://joshuajwoo.github.io/disclosure_gap/`. It is a static export with no API, database, durable participant records, or deployment secrets. `.github/workflows/pages.yml` sets:

- `GITHUB_PAGES=true`
- `NEXT_PUBLIC_DEMO_MODE=true`

The workflow builds the repository-relative base path, scans the exact deployable directory, and uploads it through GitHub's Pages actions. GitHub terminates TLS and redirects HTTP to HTTPS. `.github/workflows/monitor-pages.yml` checks the HTTPS endpoint and synthetic marker hourly; quiet matching prevents the response body from being printed. The public release must remain separate from any future research project, database, network, and secret namespace.

## Release and rollback

1. Merge or push a reviewed commit to `main`; CI and the Pages workflow must both pass.
2. Record the source commit from the Pages deployment run.
3. Verify HTTPS/redirect behavior, the synthetic banner, desktop and mobile deletion flows, network isolation, and the delivered-asset scan.
4. For a public-demo regression, revert the faulty commit with a new reviewed commit so the workflow redeploys the previous known-good static content.
5. Run the monitoring workflow manually after a rollback and confirm its success.

If a separate API-backed environment is ever approved, build immutable images, migrate with the migrator role before shifting traffic, retain the previous image digest, and use forward database repairs rather than automatic downgrades. Those procedures do not apply to the current static portfolio deployment.

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
