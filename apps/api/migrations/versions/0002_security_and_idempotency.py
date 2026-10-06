"""Add authentication, idempotency, and export-audit controls."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("participants") as batch:
        batch.add_column(sa.Column("session_token_hash", sa.String(64)))
        batch.create_unique_constraint("uq_participants_session_token_hash", ["session_token_hash"])

    with op.batch_alter_table("assessments") as batch:
        batch.add_column(sa.Column("idempotency_key", sa.String(64)))
        batch.add_column(sa.Column("payload_hash", sa.String(64)))
        batch.create_unique_constraint(
            "uq_assessments_participant_idempotency", ["participant_id", "idempotency_key"]
        )

    with op.batch_alter_table("check_ins") as batch:
        batch.add_column(sa.Column("idempotency_key", sa.String(64)))
        batch.add_column(sa.Column("payload_hash", sa.String(64)))
        batch.create_unique_constraint(
            "uq_check_ins_participant_idempotency", ["participant_id", "idempotency_key"]
        )

    op.create_table(
        "export_audits",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("export_version", sa.String(24), nullable=False),
        sa.Column("schema_fingerprint", sa.String(64), nullable=False),
        sa.Column("created_by_role", sa.String(32), nullable=False),
        sa.Column("source_contract_versions", sa.JSON(), nullable=False),
        sa.Column("row_counts", sa.JSON(), nullable=False),
        sa.Column("artifact_digest", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("export_audits")
    with op.batch_alter_table("check_ins") as batch:
        batch.drop_constraint("uq_check_ins_participant_idempotency", type_="unique")
        batch.drop_column("payload_hash")
        batch.drop_column("idempotency_key")
    with op.batch_alter_table("assessments") as batch:
        batch.drop_constraint("uq_assessments_participant_idempotency", type_="unique")
        batch.drop_column("payload_hash")
        batch.drop_column("idempotency_key")
    with op.batch_alter_table("participants") as batch:
        batch.drop_constraint("uq_participants_session_token_hash", type_="unique")
        batch.drop_column("session_token_hash")
