"""Validate and summarize the frozen SENTINEL study partition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinel_experiments.study_design import audit_study_partition

ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments" / "protocol"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    design = json.loads((PROTOCOL / "pairwise_design.json").read_text())
    confirmatory = json.loads((PROTOCOL / "confirmatory_protocol.json").read_text())
    partition = json.loads((PROTOCOL / "study_partition.json").read_text())
    report = audit_study_partition(design, confirmatory, partition)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
