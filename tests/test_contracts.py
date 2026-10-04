import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).parents[1]
CONTRACTS = ROOT / "packages" / "contracts" / "v1"


@pytest.mark.parametrize(
    "filename",
    [
        "enrollment.schema.json",
        "baseline-context.schema.json",
        "assessment.schema.json",
        "check-in.schema.json",
        "trends.schema.json",
    ],
)
def test_contract_schema_is_valid_draft_2020_12(filename: str) -> None:
    schema = json.loads((CONTRACTS / filename).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_check_in_contract_enforces_skip_logic() -> None:
    schema = json.loads((CONTRACTS / "check-in.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    valid = {
        "contractVersion": "1.0.0-draft",
        "week": 1,
        "wantedToShare": "no",
        "completedAt": "2026-10-03T12:00:00Z",
    }
    validator.validate(valid)

    invalid = {**valid, "intendedAudience": "friend"}
    with pytest.raises(ValidationError):
        validator.validate(invalid)


def test_check_in_contract_requires_followups_when_wanted() -> None:
    schema = json.loads((CONTRACTS / "check-in.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    with pytest.raises(ValidationError):
        validator.validate(
            {
                "contractVersion": "1.0.0-draft",
                "week": 2,
                "wantedToShare": "yes",
                "completedAt": "2026-10-03T12:00:00Z",
            }
        )


def test_feature_contract_has_one_primary_feature() -> None:
    contract = json.loads((CONTRACTS / "features.json").read_text(encoding="utf-8"))
    primary = [feature for feature in contract["features"] if feature["status"] == "primary"]
    assert [feature["name"] for feature in primary] == ["intention_action_gap"]


def test_assessment_contract_fixes_instrument_and_item_order() -> None:
    schema = json.loads((CONTRACTS / "assessment.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    payload = {
        "contractVersion": "1.0.0-draft",
        "assessmentType": "baseline",
        "instrumentName": "apa_dsm5tr_sad_adult",
        "instrumentVersion": "DSM-5-TR-2022",
        "language": "en",
        "responses": [
            {"itemCode": f"SAD{item:02d}", "responseCode": item % 5} for item in range(1, 11)
        ],
        "completedAt": "2026-10-04T12:00:00Z",
    }
    validator.validate(payload)

    payload["responses"][0]["itemCode"] = "SAD02"
    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_instrument_contract_records_permission_and_scoring() -> None:
    instrument = json.loads((CONTRACTS / "instrument.json").read_text(encoding="utf-8"))
    assert instrument["researchReproductionPermission"] is True
    assert instrument["itemCodesInOrder"] == [f"SAD{item:02d}" for item in range(1, 11)]
    assert instrument["scoring"]["range"] == [0, 40]
    assert "7 or fewer" in instrument["scoring"]["missing"]
