"""Validate the anonymous package and write its non-readiness audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinel_experiments.submission_integrity import check_submission_package

ROOT = Path(__file__).parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "paper/submission/submission_audit.json",
    )
    args = parser.parse_args()
    report = check_submission_package(ROOT)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
