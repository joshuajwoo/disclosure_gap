FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY requirements.lock pyproject.toml ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock

COPY apps/api ./apps/api
COPY packages/contracts ./packages/contracts

WORKDIR /workspace/apps/api
CMD ["sh", "-c", "DATABASE_URL=$MIGRATION_DATABASE_URL alembic upgrade head && uvicorn disclosure_gap_api.main:app --host 0.0.0.0 --port 8000"]
