# API service

Owns authenticated participant endpoints, exact-version validation, persistence, lifecycle constraints, deletion, and safe operational events. The public portfolio environment is synthetic-only. The service must reject unsupported contract versions explicitly and must never log sensitive response bodies or recovery credentials.

## Implemented routes

- `GET /health`
- `POST /v1/participants`
- `POST /v1/sessions/recover`
- `POST /v1/baseline-context`
- `POST /v1/assessments`
- `POST /v1/check-ins`
- `GET /v1/me/trends`
- `DELETE /v1/me`

Enrollment returns an opaque session token and a recovery code once. Send the session as `Authorization: Bearer <token>`; baseline-context, assessment, and check-in writes also require an `Idempotency-Key`. Only hashes are stored. The API derives participant scope from the token and ignores client timestamps for study-window enforcement.

From the repository root, `make dev` starts PostgreSQL, applies migrations with the local migrator role, and runs the API with a separate runtime role. The example credentials are synthetic local defaults only.
