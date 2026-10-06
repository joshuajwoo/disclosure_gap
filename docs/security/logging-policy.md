# Logging and audit-event policy

Application request logs may contain only timestamp, HTTP method, route template/path, response status, latency, environment, and a random request ID. They must never contain authorization headers, session or recovery credentials, request/response bodies, questionnaire responses, participant IDs, database URLs, stack traces returned to clients, or concern content.

The `study_events` table is restricted to this allowlist:

- `submission_accepted`
- `submission_rejected`
- `withdrawal_requested`
- `deletion_completed`
- `session_recovered`

Each event may contain only its random event ID, optional random participant ID, event type, coarse route code, coarse result code, and server timestamp. `route_code` and `result_code` are enumerated application labels, not free-text error messages. Audit events must not duplicate response payloads or secrets.

Malformed unauthenticated requests are represented by aggregate service metrics rather than participant audit rows. Authenticated domain failures such as closed windows, conflicts, duplicates, and unsupported contracts receive allowlisted rejection events.

Production ingress, platform, database, and error-reporting configuration must be reviewed separately because application-level redaction cannot prevent an upstream proxy from recording headers or bodies. Access to operational logs is role-limited and shorter-lived than approved compliance records.
