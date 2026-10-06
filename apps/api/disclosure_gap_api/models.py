from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative metadata used by Alembic and the API."""


def new_id() -> str:
    return str(uuid.uuid4())


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (
        CheckConstraint("age_band IN ('18_19', '20_22')", name="ck_participants_age_band"),
        CheckConstraint(
            "withdrawal_state IN ('active', 'withdrawal_requested', 'deleted')",
            name="ck_participants_withdrawal_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    age_band: Mapped[str] = mapped_column(String(8), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(24), nullable=False)
    recovery_code_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    session_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    withdrawal_state: Mapped[str] = mapped_column(String(24), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    consent_events: Mapped[list[ConsentEvent]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )
    baseline_context: Mapped[BaselineContext | None] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )
    assessments: Mapped[list[Assessment]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )
    check_ins: Mapped[list[CheckIn]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )
    study_events: Mapped[list[StudyEvent]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )


class ConsentEvent(Base):
    __tablename__ = "consent_events"
    __table_args__ = (
        CheckConstraint("action IN ('agree', 'withdraw')", name="ck_consent_events_action"),
        Index("ix_consent_events_participant_occurred", "participant_id", "occurred_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=False
    )
    consent_version: Mapped[str] = mapped_column(String(24), nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    participant: Mapped[Participant] = relationship(back_populates="consent_events")


class BaselineContext(Base):
    __tablename__ = "baseline_contexts"
    __table_args__ = (
        CheckConstraint(
            "support_confidence IS NULL OR support_confidence BETWEEN 1 AND 5",
            name="ck_baseline_contexts_support",
        ),
        CheckConstraint(
            "everyday_comfort IS NULL OR everyday_comfort BETWEEN 1 AND 5",
            name="ck_baseline_contexts_everyday",
        ),
        CheckConstraint(
            "insecurity_comfort IS NULL OR insecurity_comfort BETWEEN 1 AND 5",
            name="ck_baseline_contexts_insecurity",
        ),
        UniqueConstraint("participant_id", name="uq_baseline_contexts_participant"),
        UniqueConstraint(
            "participant_id",
            "idempotency_key",
            name="uq_baseline_contexts_participant_idempotency",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=False
    )
    contract_version: Mapped[str] = mapped_column(String(24), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(64))
    payload_hash: Mapped[str | None] = mapped_column(String(64))
    support_confidence: Mapped[int | None] = mapped_column(Integer)
    support_confidence_nonresponse: Mapped[str | None] = mapped_column(String(32))
    everyday_comfort: Mapped[int | None] = mapped_column(Integer)
    everyday_comfort_nonresponse: Mapped[str | None] = mapped_column(String(32))
    insecurity_comfort: Mapped[int | None] = mapped_column(Integer)
    insecurity_comfort_nonresponse: Mapped[str | None] = mapped_column(String(32))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    participant: Mapped[Participant] = relationship(back_populates="baseline_context")


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "assessment_type IN ('baseline', 'follow_up')",
            name="ck_assessments_type",
        ),
        CheckConstraint(
            "instrument_name = 'apa_dsm5tr_sad_adult' AND "
            "instrument_version = 'DSM-5-TR-2022' AND language = 'en'",
            name="ck_assessments_instrument",
        ),
        CheckConstraint(
            "total_score IS NULL OR total_score BETWEEN 0 AND 40",
            name="ck_assessments_total_score",
        ),
        UniqueConstraint(
            "participant_id", "assessment_type", name="uq_assessments_participant_type"
        ),
        UniqueConstraint(
            "participant_id", "idempotency_key", name="uq_assessments_participant_idempotency"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=False
    )
    assessment_type: Mapped[str] = mapped_column(String(16), nullable=False)
    instrument_name: Mapped[str] = mapped_column(String(80), nullable=False)
    instrument_version: Mapped[str] = mapped_column(String(40), nullable=False)
    language: Mapped[str] = mapped_column(String(12), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(24), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(64))
    payload_hash: Mapped[str | None] = mapped_column(String(64))
    item_responses: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    total_score: Mapped[int | None] = mapped_column(Integer)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    participant: Mapped[Participant] = relationship(back_populates="assessments")


class CheckIn(Base):
    __tablename__ = "check_ins"
    __table_args__ = (
        CheckConstraint("week BETWEEN 1 AND 4", name="ck_check_ins_week"),
        CheckConstraint(
            "wanted_to_share IN ('yes', 'no', 'not_sure', 'prefer_not_to_answer')",
            name="ck_check_ins_wanted",
        ),
        CheckConstraint(
            "(wanted_to_share = 'yes') OR "
            "(intended_audience IS NULL AND sharing_action IS NULL AND "
            "expected_comfort IS NULL AND anticipated_judgment IS NULL AND "
            "support_confidence IS NULL AND concern_category IS NULL)",
            name="ck_check_ins_skip_logic",
        ),
        CheckConstraint(
            "expected_comfort IS NULL OR expected_comfort BETWEEN 1 AND 5",
            name="ck_check_ins_comfort",
        ),
        CheckConstraint(
            "support_confidence IS NULL OR support_confidence BETWEEN 1 AND 5",
            name="ck_check_ins_support",
        ),
        UniqueConstraint("participant_id", "week", name="uq_check_ins_participant_week"),
        UniqueConstraint(
            "participant_id", "idempotency_key", name="uq_check_ins_participant_idempotency"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=False
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    contract_version: Mapped[str] = mapped_column(String(24), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(64))
    payload_hash: Mapped[str | None] = mapped_column(String(64))
    wanted_to_share: Mapped[str] = mapped_column(String(24), nullable=False)
    intended_audience: Mapped[str | None] = mapped_column(String(32))
    sharing_action: Mapped[str | None] = mapped_column(String(32))
    expected_comfort: Mapped[int | None] = mapped_column(Integer)
    expected_comfort_nonresponse: Mapped[str | None] = mapped_column(String(32))
    anticipated_judgment: Mapped[str | None] = mapped_column(String(32))
    support_confidence: Mapped[int | None] = mapped_column(Integer)
    support_confidence_nonresponse: Mapped[str | None] = mapped_column(String(32))
    concern_category: Mapped[str | None] = mapped_column(String(32))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    participant: Mapped[Participant] = relationship(back_populates="check_ins")


class StudyEvent(Base):
    __tablename__ = "study_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('submission_rejected', 'submission_accepted', "
            "'withdrawal_requested', 'deletion_completed', 'session_recovered')",
            name="ck_study_events_allowlist",
        ),
        Index("ix_study_events_participant_occurred", "participant_id", "occurred_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    participant_id: Mapped[str | None] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    route_code: Mapped[str | None] = mapped_column(String(32))
    result_code: Mapped[str | None] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    participant: Mapped[Participant | None] = relationship(back_populates="study_events")


class ExportAudit(Base):
    __tablename__ = "export_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    export_version: Mapped[str] = mapped_column(String(24), nullable=False)
    schema_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by_role: Mapped[str] = mapped_column(String(32), nullable=False)
    source_contract_versions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    row_counts: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)
    provenance: Mapped[dict[str, str] | None] = mapped_column(JSON)
    artifact_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
