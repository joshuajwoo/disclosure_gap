# Restricted research export design

There is no public or participant-facing export endpoint. An export is an offline, manually invoked operation available only to an authorized research-export role in an approved environment.

## Authorization workflow

1. Record the approved purpose, protocol/version, requester, minimum fields, date range, destination, retention date, and disclosure reviewer.
2. Use a short-lived export identity with read access only to approved source views and append access to `export_audits`.
3. Build into encrypted temporary storage outside the web root; validate before release.
4. Transfer only to the approved restricted analysis environment and delete the temporary copy.
5. Record artifact digest, schema fingerprint, export version, source contract versions, creation time, role, and table row counts—never participant answers—in `export_audits`.

## Allowed content

Only analysis-required structured responses, coarse/rebased study timing, an export-specific random analysis ID, explicit missing-value codes, and schema/survey/instrument/feature versions may be included. Session hashes, recovery hashes, operational participant IDs, consent/audit rows, request IDs, IP/user-agent data, database IDs, exact enrollment timestamps, and free text are prohibited.

The export validator must check field allowlists, uniqueness, joins, temporal ordering, supported versions, withdrawal/deletion exclusions, small-cell risk, and the absence of credential/operational fields. A schema fingerprint identifies interpretation; an artifact digest identifies the exact bytes.

The `export_audits` table stores provenance only and deliberately has no downloadable artifact path or public route. The implemented manual workflow and its validation tests remain separate from the static public deployment.
