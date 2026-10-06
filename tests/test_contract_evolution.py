import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text

from apps.api.disclosure_gap_api.contract_versions import (
    UnsupportedContractVersionError,
    schema_fingerprint,
    to_export_envelope,
    to_feature_input,
    validate_check_in,
)

ROOT = Path(__file__).parents[1]
PAYLOADS = ROOT / "packages/contracts/fixtures/payloads"
SCHEMAS = {
    "1.0.0-draft": ROOT / "packages/contracts/v1/check-in.schema.json",
    "1.1.0-fixture": ROOT / "packages/contracts/fixtures/v1_1/check-in.schema.json",
}


def load_json(path: Path) -> dict[str, object]:
    value: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    return value


@pytest.mark.parametrize(
    ("payload_name", "version"),
    [
        ("check-in-v1.json", "1.0.0-draft"),
        ("check-in-v1_1.json", "1.1.0-fixture"),
    ],
)
def test_each_supported_payload_uses_its_exact_schema(payload_name: str, version: str) -> None:
    payload = load_json(PAYLOADS / payload_name)
    schema = load_json(SCHEMAS[version])
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)


def test_compatible_versions_preserve_identity_through_feature_and_export_boundaries() -> None:
    v1 = validate_check_in(load_json(PAYLOADS / "check-in-v1.json"))
    v1_1 = validate_check_in(load_json(PAYLOADS / "check-in-v1_1.json"))

    v1_feature = to_feature_input(v1)
    v1_1_feature = to_feature_input(v1_1)
    assert v1_feature | {"source_contract_version": "ignored"} == v1_1_feature | {
        "source_contract_version": "ignored"
    }
    assert v1_feature["source_contract_version"] == "1.0.0-draft"
    assert v1_1_feature["source_contract_version"] == "1.1.0-fixture"

    v1_export = to_export_envelope(v1)
    v1_1_export = to_export_envelope(v1_1)
    assert v1_export["contract_version"] == "1.0.0-draft"
    assert v1_1_export["contract_version"] == "1.1.0-fixture"
    assert v1_export["schema_fingerprint"] != v1_1_export["schema_fingerprint"]
    assert v1_export["schema_fingerprint"] == schema_fingerprint("1.0.0-draft")
    assert v1_1_export["schema_fingerprint"] == schema_fingerprint("1.1.0-fixture")


def test_unknown_version_fails_before_response_codes_can_be_reinterpreted() -> None:
    payload = load_json(PAYLOADS / "check-in-unsupported.json")
    with pytest.raises(
        UnsupportedContractVersionError,
        match=r"unsupported check-in contract version: '2\.0\.0-unsupported'",
    ):
        validate_check_in(payload)


def test_feature_projection_preserves_nonsharing_reason_semantics() -> None:
    payload = load_json(PAYLOADS / "check-in-v1.json")
    payload["sharingAction"] = "no_safe_opportunity"
    projected = to_feature_input(validate_check_in(payload))
    assert projected["sharing_action"] == "no_safe_opportunity"
    assert projected["shared"] is None


def test_migrated_schema_preserves_both_exact_contract_versions(tmp_path: Path) -> None:
    database_path = tmp_path / "evolution.sqlite"
    database_url = f"sqlite:///{database_path}"
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT / "apps/api",
        env=os.environ | {"DATABASE_URL": database_url},
        check=True,
        capture_output=True,
        text=True,
    )

    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO participants "
                "(id, age_band, contract_version, withdrawal_state) "
                "VALUES ('participant-1', '18_19', '1.0.0-draft', 'active')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO check_ins "
                "(id, participant_id, week, contract_version, wanted_to_share, completed_at) "
                "VALUES "
                "('check-in-1', 'participant-1', 1, '1.0.0-draft', 'no', "
                "'2026-10-04T12:00:00Z'), "
                "('check-in-2', 'participant-1', 2, '1.1.0-fixture', 'no', "
                "'2026-10-11T12:00:00Z')"
            )
        )
        versions = connection.execute(
            text("SELECT contract_version FROM check_ins ORDER BY week")
        ).scalars()
        assert list(versions) == ["1.0.0-draft", "1.1.0-fixture"]
