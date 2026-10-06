# The Disclosure Gap

[Open the synthetic public demo](https://joshuajwoo.github.io/disclosure_gap/) · [Read the engineering case study](docs/release/engineering-case-study.md)

A privacy-first longitudinal software project built around a personally meaningful question: how can a system responsibly represent the moments when someone wants support from a trusted person but decides not to ask for it?

The disclosure question is a case study, not a claim of a new psychological discovery. Social anxiety, avoidance, self-disclosure, and help-seeking already have substantial research literatures. The primary contribution here is the engineering system: versioned data collection, temporal and integrity constraints, consent and deletion workflows, restricted exports, documented feature lineage, deterministic synthetic cohorts, and reproducible analysis.

The public portfolio path uses synthetic data. Synthetic estimates test whether the software behaves as designed; they are never findings about people. A small real-data pilot is optional and may proceed only after institutional, consent, security, and readiness gates are cleared. Any such analysis would be limited and exploratory unless its design and sample justified otherwise.

See [`PLAN.md`](PLAN.md) for the project framing and [`docs/protocol/README.md`](docs/protocol/README.md) for the boundary between synthetic validation and optional empirical work.

## What this project demonstrates

- versioned survey, instrument, database, export, and feature contracts;
- correct handling of repeated measurements, sparse denominators, missingness, and attrition;
- privacy workflows including data minimization, withdrawal, and deletion;
- deterministic pipeline validation across null, effect, confounded, and schema-change scenarios; and
- a reproducible path from structured records to clearly labeled tables and figures.

It is not a diagnostic or treatment product, a judgment about choosing privacy, a system for inferring undisclosed feelings, or population-level evidence.

## Repository map

- `apps/web`: participant-facing Next.js application
- `apps/api`: FastAPI service and persistence layer
- `packages/contracts`: versioned survey and feature contracts
- `research`: synthetic generation, export, ETL, features, analysis, and reports
- `infra`: local and deployment infrastructure
- `docs/protocol`: case-study, measurement, ethics, and governance documents
- `tests`: cross-component and critical-flow tests

## Prerequisites

- Node.js 22.14.0 and npm 10.9.2
- Python 3.12.3
- Docker 28+ with Docker Compose 2.35+

## Commands

Run `make help` for the canonical command list. The principal commands are:

```text
make setup       install JavaScript and Python dependencies
make dev         start the local Docker Compose stack
make lint        run repository static checks
make typecheck   run TypeScript and Python type checks
make test        run unit tests
make e2e         run Playwright tests
make check       run lint, type checks, and unit tests
make migrate     apply database migrations
make synthetic   generate and validate deterministic synthetic cohorts
make report      rebuild validated synthetic tables, figures, and report
make release-check build and scan the synthetic public web artifact
```

The API serves `/health` and versioned participant routes under `/v1`. See [`apps/api/README.md`](apps/api/README.md) for the endpoint and authentication summary. Generated synthetic records are written beneath ignored `data/synthetic/`; they are pipeline fixtures, not empirical results.

`make report` writes ignored artifacts beneath `reports/generated/`. Every report and figure is labeled `SYNTHETIC — PIPELINE VALIDATION ONLY`. The restricted real-data export is a manual, role-gated Python workflow with no public API route; its institutional and production-security gates remain closed.

Release and operating material is in [`docs/release`](docs/release), the [operations runbook](docs/operations/runbook.md), and the [system card](docs/system-card.md). A public deployment still requires a user-selected hosting project, domain or provider URL, deployment credentials, HTTPS configuration, and privacy-safe monitoring.

## Safety boundary

Do not enter, import, or deploy real participant data. Do not recruit participants until the review gates in [`docs/protocol/review-requirements.md`](docs/protocol/review-requirements.md) are formally cleared. Public demos and committed fixtures must remain synthetic and unmistakably labeled.
