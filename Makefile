.DEFAULT_GOAL := help
PYTHON ?= .venv/bin/python

.PHONY: help setup dev stop lint typecheck test e2e check migrate synthetic report release-check

help:
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install pinned JavaScript and Python dependencies
	npm ci
	python3 -m venv .venv
	.venv/bin/python -m pip install --require-hashes -r requirements.lock

dev: ## Start web, API, and PostgreSQL through Docker Compose
	docker compose -f infra/compose.yaml up --build

stop: ## Stop the local Docker Compose stack
	docker compose -f infra/compose.yaml down

lint: ## Run Markdown, YAML, TypeScript, and Python linters
	npm run lint
	.venv/bin/ruff format --check .
	.venv/bin/ruff check .

typecheck: ## Run TypeScript and Python type checks
	npx tsc --noEmit
	.venv/bin/mypy apps/api/disclosure_gap_api research

test: ## Run Python unit tests
	.venv/bin/pytest

e2e: ## Run Playwright critical-flow tests
	npx playwright test

check: lint typecheck test ## Run all non-browser quality checks

migrate: ## Apply database migrations
	@test -f apps/api/alembic.ini || (echo "Migrations are not implemented yet (DAT-05)." && exit 1)
	cd apps/api && ../../.venv/bin/alembic upgrade head

synthetic: ## Generate deterministic synthetic study data
	@test -f research/generate_synthetic.py || (echo "Synthetic generation is not implemented yet (SYN-02)." && exit 1)
	$(PYTHON) -m research.generate_synthetic

report: ## Rebuild research tables, figures, and report
	@test -f research/build_report.py || (echo "Report generation is not implemented yet (ANA-11)." && exit 1)
	$(PYTHON) -m research.build_report

release-check: ## Build and scan the synthetic public web artifact
	npm run build --workspace apps/web
	$(PYTHON) scripts/verify_public_artifact.py
