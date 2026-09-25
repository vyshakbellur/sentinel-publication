"""Verify and analyze one immutable SENTINEL run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinel_experiments.run_analysis import analyze_run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirmatory", action="store_true")
    args = parser.parse_args()
    report = analyze_run(args.run_dir, confirmatory=args.confirmatory)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
