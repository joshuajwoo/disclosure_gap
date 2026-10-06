"""Validated loading for versioned research exports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from research.export import validate_export

SUPPORTED_CONTRACT_VERSIONS = {"1.0.0-draft", "1.1.0-fixture"}


@dataclass(frozen=True)
class AnalysisTables:
    manifest: dict[str, object]
    participants: pl.DataFrame
    baseline_contexts: pl.DataFrame
    assessments: pl.DataFrame
    check_ins: pl.DataFrame


def load_export(path: Path) -> AnalysisTables:
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    versions = set(manifest["sourceContractVersions"])
    unsupported = versions - SUPPORTED_CONTRACT_VERSIONS
    if unsupported:
        raise ValueError(f"unsupported contract mapping: {sorted(unsupported)}")
    tables = validate_export(path)
    return AnalysisTables(
        manifest=manifest,
        participants=tables["participants"],
        baseline_contexts=tables["baseline_contexts"],
        assessments=tables["assessments"],
        check_ins=tables["check_ins"],
    )
