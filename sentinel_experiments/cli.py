"""Command-line entry point for the initial SENTINEL experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .campaign import campaign_specs
from .harness import run_matrix
from .matrix import baseline_matrix, initial_matrix, policy_baseline_matrix
from .reporting import summarize, write_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--matrix",
        choices=("initial", "baseline", "policy-baseline", "campaign"),
        default="initial",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    matrices = {
        "initial": initial_matrix,
        "baseline": baseline_matrix,
        "policy-baseline": policy_baseline_matrix,
    }
    if args.matrix == "campaign":
        protocol_dir = Path(__file__).parents[1] / "experiments" / "protocol"
        campaign = json.loads((protocol_dir / "campaign_plan.json").read_text())
        specs = campaign_specs(campaign)
    else:
        specs = matrices[args.matrix]()
    records = run_matrix(specs)
    write_run(args.output, specs, records)
    print(json.dumps(summarize(records), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
