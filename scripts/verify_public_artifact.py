"""Fail when a synthetic public web build contains known private configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

PROHIBITED = (
    b"postgresql+psycopg://",
    b"local_admin_only",
    b"local_runtime_only",
    b"local_migration_only",
    b"MIGRATION_DATABASE_URL",
    b"REAL_DATA_READINESS_APPROVED=true",
    b"ALLOW_REAL_PARTICIPANT_DATA=true",
    b"http://localhost:8000",
    b"BEGIN PRIVATE KEY",
)


def verify(build_dir: Path) -> list[str]:
    if not build_dir.is_dir():
        raise FileNotFoundError(f"web build not found: {build_dir}")
    findings: list[str] = []
    for path in build_dir.rglob("*"):
        if not path.is_file() or path.suffix == ".map":
            continue
        content = path.read_bytes()
        for marker in PROHIBITED:
            if marker in content:
                findings.append(f"{path}: contains {marker.decode(errors='replace')}")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dirs", type=Path, nargs="*")
    args = parser.parse_args()
    build_dirs = args.build_dirs or [
        Path("apps/web/.next/static"),
        Path("apps/web/.next/standalone"),
    ]
    findings = [finding for build_dir in build_dirs for finding in verify(build_dir)]
    if findings:
        raise SystemExit("Public artifact safety check failed:\n" + "\n".join(findings))
    print("Public artifact safety check passed (synthetic build; no prohibited markers).")


if __name__ == "__main__":
    main()
