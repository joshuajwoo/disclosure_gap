# Contract-evolution proof

This repository treats contract versions as data. Stored records, feature inputs, and export envelopes retain the exact source version so a later schema cannot silently reinterpret an earlier response.

## Exercised versions

- `1.0.0-draft` is the current synthetic-only check-in contract in `v1/check-in.schema.json`.
- `1.1.0-fixture` is a CI-only evolution fixture in `fixtures/v1_1/check-in.schema.json`. It adds the optional UUID `clientSubmissionId` while leaving every existing response code and skip rule unchanged. An old payload therefore remains valid in meaning, and both versions deliberately map to the same feature inputs.

The fixture version is not a release candidate and must not be accepted accidentally by treating all `1.x` values as interchangeable. Each supported version has an explicit validator, schema path, and mapping entry.

## Compatibility rules

Compatible changes may add an optional field that has no effect on existing feature meaning, clarify documentation, or tighten implementation without rejecting previously valid data. They still require a new version and a deliberate registry entry.

Incompatible changes include renaming or repurposing a response code, changing skip logic, changing the meaning of a numeric scale, making an optional field required, or changing a feature denominator. For example, replacing `chose_private` with `kept_private` is not an alias: it requires a new documented mapping and migration decision. The committed unsupported payload proves that an unknown version fails explicitly before normalization.

## Boundaries exercised in CI

`apps/api/disclosure_gap_api/contract_versions.py` is the shared API version boundary. It dispatches exact versions to typed validation and projects only documented values into versioned feature input. The restricted export preserves exact source versions and a SHA-256 schema fingerprint, while ETL rejects unknown mappings. Tests exercise both versions through persistence, export, and feature construction.

No layer may fall back to the newest schema, guess aliases, or discard the source version.
