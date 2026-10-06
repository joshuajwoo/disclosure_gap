from __future__ import annotations

from pathlib import Path
from typing import Any


class DataBoundaryError(ValueError):
    """Raised when an artifact could cross the synthetic/public boundary."""


def assert_synthetic_dataset(dataset: dict[str, Any]) -> None:
    if dataset.get("metadata", {}).get("synthetic") is not True:
        raise DataBoundaryError("public/demo artifacts require metadata.synthetic=true")
    for cohort in dataset.get("cohorts", []):
        if cohort.get("metadata", {}).get("synthetic") is not True:
            raise DataBoundaryError("every cohort must be explicitly synthetic")
        if any(record.get("synthetic") is not True for record in cohort.get("participants", [])):
            raise DataBoundaryError("every participant record must be explicitly synthetic")


def assert_safe_generated_output(path: Path, workspace: Path) -> None:
    resolved = path.resolve()
    allowed = (workspace / "data/synthetic").resolve()
    if not resolved.is_relative_to(allowed):
        raise DataBoundaryError("synthetic generator output must stay under data/synthetic")
