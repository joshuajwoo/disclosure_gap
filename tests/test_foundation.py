from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_required_repository_areas_have_readmes() -> None:
    areas = (
        "apps/web",
        "apps/api",
        "packages/contracts",
        "research",
        "infra",
        "docs",
        "tests",
    )
    assert all((ROOT / area / "README.md").is_file() for area in areas)


def test_example_environment_defaults_to_synthetic_only() -> None:
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "APP_ENV=local-synthetic" in example
    assert "ALLOW_REAL_PARTICIPANT_DATA=false" in example


def test_protocol_controls_exist() -> None:
    required = (
        "preregistration.md",
        "instrument-decision.md",
        "survey.md",
        "predictor-outcome-overlap.md",
        "participant-language.md",
        "consent.md",
        "review-requirements.md",
        "data-dictionary.md",
        "limitations.md",
    )
    protocol = ROOT / "docs/protocol"
    assert all((protocol / name).is_file() for name in required)
