# Record lifecycle constraints

Version: 1.0.0-draft; synthetic-only until review gates clear.

## Schedule

The authoritative scheduler will derive windows from an enrollment/study-start instant in UTC. Exact grace periods must be approved before recruitment. Baseline is accepted once before week 1; check-ins are accepted once in each of four non-overlapping weekly windows; follow-up is accepted once after the fourth window. Client timestamps never determine eligibility—the API records server receipt/completion time.

## Uniqueness and transitions

- One participant row per opaque enrollment; duplicate-detection methods may not introduce identity fields without approved amendment.
- One immutable consent event for agreement; withdrawal appends an event rather than overwriting history.
- At most one baseline and one follow-up assessment per participant.
- At most one check-in per participant/week. A retry with the same idempotency key must return the existing result; a conflicting second payload is rejected.
- Active participants may submit in an open window. `withdrawal_requested` and `deleted` participants may not submit or view trends.
- Follow-up cannot precede baseline. Feature code excludes check-ins at or after follow-up regardless of week label.

## Corrections and deletion

Submitted research responses are immutable in v1. Corrections require an approved append-only amendment design. Withdrawal initiates the separately approved deletion workflow. Hard deletion cascades participant-linked consent, assessment, check-in, and event rows; any compliance record that must legally remain must be separated and justified before real deployment. Backups and already-aggregated outputs follow the approved retention policy.

## Failure behavior

Invalid versions, closed windows, duplicates, impossible skip patterns, and withdrawn sessions are rejected without storing response bodies in logs. Database uniqueness/check constraints are the final concurrency guard; API validation is not the only control.
