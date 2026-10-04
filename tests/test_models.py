from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.disclosure_gap_api.models import Assessment, Base, CheckIn, Participant


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as database_session:
        yield database_session


def participant() -> Participant:
    return Participant(
        age_band="18_19",
        contract_version="1.0.0-draft",
        recovery_code_hash="not-a-real-hash",
    )


def test_one_check_in_per_participant_week(session: Session) -> None:
    record = participant()
    session.add(record)
    session.flush()
    now = datetime.now(UTC)
    session.add_all(
        [
            CheckIn(
                participant_id=record.id,
                week=1,
                contract_version="1.0.0-draft",
                wanted_to_share="no",
                completed_at=now,
            ),
            CheckIn(
                participant_id=record.id,
                week=1,
                contract_version="1.0.0-draft",
                wanted_to_share="no",
                completed_at=now,
            ),
        ]
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_skip_logic_rejects_followup_fields_when_not_wanted(session: Session) -> None:
    record = participant()
    session.add(record)
    session.flush()
    session.add(
        CheckIn(
            participant_id=record.id,
            week=1,
            contract_version="1.0.0-draft",
            wanted_to_share="no",
            intended_audience="friend",
            completed_at=datetime.now(UTC),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_assessment_constraint_fixes_instrument_and_score_range(session: Session) -> None:
    record = participant()
    session.add(record)
    session.flush()
    session.add(
        Assessment(
            participant_id=record.id,
            assessment_type="baseline",
            instrument_name="wrong_instrument",
            instrument_version="DSM-5-TR-2022",
            language="en",
            contract_version="1.0.0-draft",
            item_responses=[],
            total_score=41,
            completed_at=datetime.now(UTC),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
