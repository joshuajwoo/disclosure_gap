# Fresh-environment reproduction

The reproducibility target is a synthetic-only checkout with the pinned Node and Python versions. No participant data or external credentials are required.

## Clean-checkout procedure

```bash
git clone <repository-url> disclosure_gap
cd disclosure_gap
make setup
make check
npm run build --workspace apps/web
npx playwright install chromium
make e2e
make synthetic
make report
docker compose -p disclosure-gap-reproduction -f infra/compose.yaml up --build -d
docker compose -p disclosure-gap-reproduction -f infra/compose.yaml ps
docker compose -p disclosure-gap-reproduction -f infra/compose.yaml down --volumes
```

The final command removes only the explicitly named reproduction stack and its synthetic volumes.

## Expected evidence

- lint and strict type checks succeed;
- all Python contract, API, export, feature, analysis, and safety tests pass;
- Playwright completes the synthetic flow with no live API request and no Axe violation;
- Alembic applies migrations `0001` through `0003` to an empty database;
- the web production build completes;
- `reports/generated/report.md` and its machine-readable inputs are rebuilt with the synthetic label;
- PostgreSQL and the API report healthy, and the web root returns successfully.

CI repeats dependency installation, checks, migrations, the production web build, the report rebuild, and browser tests from a fresh hosted runner. Generated records, exports, and reports remain ignored artifacts.

## Latest local reproduction

On 2026-10-04, a source-only copy with no existing `node_modules`, virtual environment, generated data, report, or container volume completed dependency installation, 47 Python tests, strict checks, the production web build, four Playwright/Axe tests, synthetic generation, report generation, migrations `0001`–`0003`, and a clean three-service Compose startup. PostgreSQL and the API became healthy and the web root responded successfully. The explicitly named containers, network, and synthetic volumes were removed afterward.
