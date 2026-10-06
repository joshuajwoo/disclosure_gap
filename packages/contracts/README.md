# Contracts

Owns versioned survey schemas, response codes, API payload definitions, and feature specifications shared across collection and analysis. Contract changes require a new version and a documented migration decision.

`v1/manifest.json` is the entry point. JSON Schema is canonical so both TypeScript and Python can validate the same wire format. Version `1.0.0-draft` remains synthetic-only until human-subjects review and real-data readiness are complete. `instrument.json` fixes the selected APA outcome, scoring, item codes, and official normative wording source; the repository does not maintain a divergent wording copy.

`evolution.md` documents the compatibility policy and the second, CI-only contract fixture used to prove exact version dispatch, persistence, feature projection, and export identity.

`v1/export.schema.json` describes the restricted research-export manifest. The export includes only allowlisted analysis fields, fresh analysis IDs, relative study days, exact source versions, row counts, provenance, a schema fingerprint, and an artifact digest. Operational IDs, credentials, payload hashes, and exact event timestamps are prohibited.
