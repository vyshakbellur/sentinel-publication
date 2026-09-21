"""Command-line entry point for the initial SENTINEL experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .harness import run_matrix
from .matrix import initial_matrix
from .reporting import summarize, write_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    specs = initial_matrix()
    records = run_matrix(specs)
    write_run(args.output, specs, records)
    print(json.dumps(summarize(records), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

