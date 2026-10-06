# Retention, withdrawal, and deletion policy

Status: implemented for synthetic/local records; institution-specific durations and backup guarantees are unresolved, so real recruitment remains blocked.

## Live-system behavior

`DELETE /v1/me` authenticates the current participant, appends withdrawal/deletion audit events, removes assessments, baseline context, and check-ins, clears session and recovery hashes, and changes the random participant row to a non-accessible `deleted` tombstone with a deletion timestamp. The tombstone retains no questionnaire response or credential and supports verification that the request completed. The prior token and recovery code stop working immediately.

Consent and minimal operational history are retained with the random tombstone only when the approved policy requires evidence of consent/withdrawal. If the responsible institution requires their deletion instead, that must be implemented and versioned before recruitment.

## Derived data and exports

The deletion workflow must search active restricted exports and derived row-level datasets by the export-specific linkage record, remove the row when still linkable, rebuild affected artifacts, and append verification to the deletion case. Anonymous aggregates may be impossible to reverse once the linkage is destroyed; approved consent must explain that boundary.

## Backups

Live deletion does not promise immediate physical erasure from immutable backups. Before real use, document backup frequency, encryption, access, restore procedure, expiry period, and how deleted records are prevented from re-entering the live system after restore. A restored database must replay the deletion ledger before serving traffic.

## Durations and verification

No real-data duration is selected by this portfolio repository. The approving institution must set durations for active responses, consent history, operational events, export audits, restricted artifacts, and backups. A deletion verification record must include request time, live-row result, credential revocation, export/derived-artifact result, backup-expiry date, operator or automated process, and final status—never the deleted answers.
