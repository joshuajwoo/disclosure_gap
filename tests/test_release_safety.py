from pathlib import Path

from scripts.verify_public_artifact import PROHIBITED, verify


def test_public_artifact_scanner_rejects_private_configuration(tmp_path: Path) -> None:
    safe = tmp_path / "safe"
    safe.mkdir()
    (safe / "app.js").write_text("SYNTHETIC DEMO", encoding="utf-8")
    assert verify(safe) == []
    (safe / "bad.js").write_bytes(b"prefix " + PROHIBITED[0] + b"secret")
    assert "postgresql+psycopg" in verify(safe)[0]


def test_source_configuration_keeps_real_data_disabled() -> None:
    root = Path(__file__).parents[1]
    example = (root / ".env.example").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_DEMO_MODE=true" in example
    assert "ALLOW_REAL_PARTICIPANT_DATA=false" in example
    assert "REAL_DATA_READINESS_APPROVED=false" in example
