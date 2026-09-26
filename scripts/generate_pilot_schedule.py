"""Generate and audit a deterministic blocked pilot schedule."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinel_experiments.scheduling import (
    audit_pilot_schedule,
    generate_pilot_schedule,
)

ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments" / "protocol"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blocks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads((PROTOCOL / "confirmatory_protocol.json").read_text())
    design = json.loads((PROTOCOL / "pairwise_design.json").read_text())
    partition = json.loads((PROTOCOL / "study_partition.json").read_text())
    blocks = json.loads(args.blocks.read_text())
    schedule = generate_pilot_schedule(protocol, design, partition, blocks)
    audit = audit_pilot_schedule(schedule, protocol, design, partition)
    args.output.write_text(
        json.dumps(schedule, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.audit_output.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
