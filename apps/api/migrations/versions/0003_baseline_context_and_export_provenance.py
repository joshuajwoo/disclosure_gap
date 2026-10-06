"""Add retry metadata and export provenance."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("baseline_contexts") as batch:
        batch.add_column(sa.Column("idempotency_key", sa.String(64)))
        batch.add_column(sa.Column("payload_hash", sa.String(64)))
        batch.create_unique_constraint(
            "uq_baseline_contexts_participant_idempotency",
            ["participant_id", "idempotency_key"],
        )
    with op.batch_alter_table("export_audits") as batch:
        batch.add_column(sa.Column("provenance", sa.JSON()))


def downgrade() -> None:
    with op.batch_alter_table("export_audits") as batch:
        batch.drop_column("provenance")
    with op.batch_alter_table("baseline_contexts") as batch:
        batch.drop_constraint("uq_baseline_contexts_participant_idempotency", type_="unique")
        batch.drop_column("payload_hash")
        batch.drop_column("idempotency_key")
