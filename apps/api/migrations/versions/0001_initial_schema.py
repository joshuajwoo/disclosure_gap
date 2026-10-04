"""Create the initial privacy-minimized study schema."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "participants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("age_band", sa.String(8), nullable=False),
        sa.Column("contract_version", sa.String(24), nullable=False),
        sa.Column("recovery_code_hash", sa.String(255)),
        sa.Column("withdrawal_state", sa.String(24), nullable=False, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("age_band IN ('18_19', '20_22')", name="ck_participants_age_band"),
        sa.CheckConstraint(
            "withdrawal_state IN ('active', 'withdrawal_requested', 'deleted')",
            name="ck_participants_withdrawal_state",
        ),
    )
    op.create_table(
        "consent_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "participant_id",
            sa.String(36),
            sa.ForeignKey("participants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("consent_version", sa.String(24), nullable=False),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("action IN ('agree', 'withdraw')", name="ck_consent_events_action"),
    )
    op.create_index(
        "ix_consent_events_participant_occurred",
        "consent_events",
        ["participant_id", "occurred_at"],
    )
    op.create_table(
        "baseline_contexts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "participant_id",
            sa.String(36),
            sa.ForeignKey("participants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("contract_version", sa.String(24), nullable=False),
        sa.Column("support_confidence", sa.Integer()),
        sa.Column("support_confidence_nonresponse", sa.String(32)),
        sa.Column("everyday_comfort", sa.Integer()),
        sa.Column("everyday_comfort_nonresponse", sa.String(32)),
        sa.Column("insecurity_comfort", sa.Integer()),
        sa.Column("insecurity_comfort_nonresponse", sa.String(32)),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "support_confidence IS NULL OR support_confidence BETWEEN 1 AND 5",
            name="ck_baseline_contexts_support",
        ),
        sa.CheckConstraint(
            "everyday_comfort IS NULL OR everyday_comfort BETWEEN 1 AND 5",
            name="ck_baseline_contexts_everyday",
        ),
        sa.CheckConstraint(
            "insecurity_comfort IS NULL OR insecurity_comfort BETWEEN 1 AND 5",
            name="ck_baseline_contexts_insecurity",
        ),
        sa.UniqueConstraint("participant_id", name="uq_baseline_contexts_participant"),
    )
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "participant_id",
            sa.String(36),
            sa.ForeignKey("participants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assessment_type", sa.String(16), nullable=False),
        sa.Column("instrument_name", sa.String(80), nullable=False),
        sa.Column("instrument_version", sa.String(40), nullable=False),
        sa.Column("language", sa.String(12), nullable=False),
        sa.Column("contract_version", sa.String(24), nullable=False),
        sa.Column("item_responses", sa.JSON(), nullable=False),
        sa.Column("total_score", sa.Integer()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "assessment_type IN ('baseline', 'follow_up')", name="ck_assessments_type"
        ),
        sa.CheckConstraint(
            "instrument_name = 'apa_dsm5tr_sad_adult' AND "
            "instrument_version = 'DSM-5-TR-2022' AND language = 'en'",
            name="ck_assessments_instrument",
        ),
        sa.CheckConstraint(
            "total_score IS NULL OR total_score BETWEEN 0 AND 40",
            name="ck_assessments_total_score",
        ),
        sa.UniqueConstraint(
            "participant_id", "assessment_type", name="uq_assessments_participant_type"
        ),
    )
    op.create_table(
        "check_ins",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "participant_id",
            sa.String(36),
            sa.ForeignKey("participants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("contract_version", sa.String(24), nullable=False),
        sa.Column("wanted_to_share", sa.String(24), nullable=False),
        sa.Column("intended_audience", sa.String(32)),
        sa.Column("sharing_action", sa.String(32)),
        sa.Column("expected_comfort", sa.Integer()),
        sa.Column("expected_comfort_nonresponse", sa.String(32)),
        sa.Column("anticipated_judgment", sa.String(32)),
        sa.Column("support_confidence", sa.Integer()),
        sa.Column("support_confidence_nonresponse", sa.String(32)),
        sa.Column("concern_category", sa.String(32)),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("week BETWEEN 1 AND 4", name="ck_check_ins_week"),
        sa.CheckConstraint(
            "wanted_to_share IN ('yes', 'no', 'not_sure', 'prefer_not_to_answer')",
            name="ck_check_ins_wanted",
        ),
        sa.CheckConstraint(
            "(wanted_to_share = 'yes') OR "
            "(intended_audience IS NULL AND sharing_action IS NULL AND "
            "expected_comfort IS NULL AND anticipated_judgment IS NULL AND "
            "support_confidence IS NULL AND concern_category IS NULL)",
            name="ck_check_ins_skip_logic",
        ),
        sa.CheckConstraint(
            "expected_comfort IS NULL OR expected_comfort BETWEEN 1 AND 5",
            name="ck_check_ins_comfort",
        ),
        sa.CheckConstraint(
            "support_confidence IS NULL OR support_confidence BETWEEN 1 AND 5",
            name="ck_check_ins_support",
        ),
        sa.UniqueConstraint("participant_id", "week", name="uq_check_ins_participant_week"),
    )
    op.create_table(
        "study_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "participant_id", sa.String(36), sa.ForeignKey("participants.id", ondelete="CASCADE")
        ),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("route_code", sa.String(32)),
        sa.Column("result_code", sa.String(32)),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "event_type IN ('submission_rejected', 'submission_accepted', "
            "'withdrawal_requested', 'deletion_completed', 'session_recovered')",
            name="ck_study_events_allowlist",
        ),
    )
    op.create_index(
        "ix_study_events_participant_occurred", "study_events", ["participant_id", "occurred_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_study_events_participant_occurred", table_name="study_events")
    op.drop_table("study_events")
    op.drop_table("check_ins")
    op.drop_table("assessments")
    op.drop_table("baseline_contexts")
    op.drop_index("ix_consent_events_participant_occurred", table_name="consent_events")
    op.drop_table("consent_events")
    op.drop_table("participants")
