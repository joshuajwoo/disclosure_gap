# The Disclosure Gap

Research software for studying whether the gap between wanting to share a personal concern and actually sharing it is associated with follow-up social-anxiety scores among adults ages 18–22.

The repository is currently in its protocol-and-foundations phase. It must use synthetic data only until the review gates in [`docs/protocol/review-requirements.md`](docs/protocol/review-requirements.md) are cleared.

## Repository map

- `apps/web`: participant-facing Next.js application
- `apps/api`: FastAPI service and persistence layer
- `packages/contracts`: versioned survey and feature contracts
- `research`: export, ETL, feature, analysis, and report code
- `infra`: local and deployment infrastructure
- `docs/protocol`: protocol, consent, measurement, and governance documents
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
make migrate     apply database migrations (available after API bootstrap)
make synthetic   generate synthetic data (available after generator implementation)
make report      rebuild research outputs (available after pipeline implementation)
```

Commands not yet implemented fail with an explanatory message rather than silently succeeding.

## Safety boundary

Do not enter, import, or deploy real participant data. Do not recruit participants until institutional review, final consent, security, and real-data-readiness gates are formally cleared.
