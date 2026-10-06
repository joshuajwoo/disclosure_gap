# Infrastructure

Owns local orchestration and deployment configuration. Synthetic/demo and real-research environments must remain separate; real-data deployment is prohibited until all readiness gates are cleared.

Local PostgreSQL uses three deliberately separate, non-secret development roles: the container administrator, a schema migrator, and a runtime API role without schema-creation permission. Production credentials must come from a deployment secret store and must not reuse these example values.

The web Dockerfile has separate development and production targets. Local Compose explicitly selects `dev`; the default final image is a non-root standalone synthetic-demo server for optional self-hosting. The current public environment is instead a scanned static export deployed by GitHub Actions to GitHub Pages. It has no API, database, deployment secrets, or path to the real-data configuration. Deployment and rollback procedures are documented in `docs/operations/runbook.md`.
