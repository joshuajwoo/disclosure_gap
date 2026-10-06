# Secrets, credentials, and environment separation

The committed `.env.example` contains local synthetic defaults only. `.env`, `data/`, and `exports/` are ignored. Real credentials, recovery/session values, participant records, and exported artifacts must never be committed or placed in frontend environment variables.

`ALLOW_REAL_PARTICIPANT_DATA=true` is rejected unless `REAL_DATA_READINESS_APPROVED=true`; synthetic, test, and public-demo environments reject real-data mode even when both values are set. These are safety interlocks, not substitutes for institutional approval or infrastructure controls.

Production requirements:

- obtain database, application, and monitoring secrets from the deployment platform’s secret store;
- use separate projects/accounts, databases, encryption keys, and service identities for public demo and any approved research environment;
- give the API only CRUD rights on application tables and no role/database administration rights;
- use a separate, time-limited migration identity and a separate manual export identity;
- prohibit browser-exposed variables from containing secrets;
- rotate credentials after suspected exposure and on the approved schedule;
- mask database URLs and credentials in CI and operational output; and
- test restore, revocation, and rotation procedures before real data.

The local Compose password is intentionally non-secret and valid only for the isolated development database.
