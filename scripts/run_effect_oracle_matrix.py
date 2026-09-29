"""Run and verify the preregistered independent-effect fault matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sentinel_experiments.effect_oracle_matrix import build_report


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _assert_acceptance(report: dict, protocol: dict) -> None:
    expected = protocol["acceptance"]
    assert report["trial_count"] == expected["trial_count"]
    assert report["native_namespace_roundtrips"] == expected["trial_count"]
    assert report["oracle_summary"] == expected["oracle"]
    assert report["comparison_status_counts"] == expected[
        "comparison_status_counts"
    ]
    assert report["comparison_counts"] == expected["comparison_counts"]


def main() -> None:
    args = _args()
    protocol_bytes = args.protocol.read_bytes()
    protocol = json.loads(protocol_bytes)
    report = build_report(protocol, hashlib.sha256(protocol_bytes).hexdigest())
    _assert_acceptance(report, protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
