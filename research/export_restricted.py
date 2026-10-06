"""Manual-only CLI for an approved restricted database export."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an audited de-identified export")
    parser.add_argument("output", type=Path)
    parser.add_argument("--role", required=True)
    parser.add_argument("--approval-id", required=True)
    parser.parse_args()
    raise SystemExit(
        "Refusing implicit database access. Invoke create_restricted_export from an approved "
        "operator session with least-privilege credentials."
    )


if __name__ == "__main__":
    main()
