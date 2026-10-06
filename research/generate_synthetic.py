from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.data_boundary import assert_safe_generated_output, assert_synthetic_dataset
from research.synthetic import generate_all, validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic pipeline-validation cohorts.")
    parser.add_argument("--seed", type=int, default=20261004)
    parser.add_argument("--size", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/cohorts.json"))
    args = parser.parse_args()

    dataset = generate_all(seed=args.seed, size=args.size)
    assert_synthetic_dataset(dataset)
    summaries = validate_dataset(dataset)
    assert_safe_generated_output(args.output, Path.cwd())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")
    print(f"wrote synthetic-only dataset to {args.output}")
    print(json.dumps(summaries, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
