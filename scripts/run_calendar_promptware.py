"""Run the preregistered synthetic stored-calendar promptware matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sentinel_experiments.calendar_promptware import build_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    content = args.protocol.read_bytes()
    protocol = json.loads(content)
    report = build_report(protocol, hashlib.sha256(content).hexdigest())
    expected = protocol["acceptance"]
    for key in (
        "trial_count",
        "fixture_count",
        "benign_fixture_count",
        "attack_fixture_count",
        "attempted_unauthorized_actions",
        "completed_unauthorized_effects",
        "total_completed_effects",
        "safe_useful_trials",
        "receipt_effect_comparisons",
        "by_guardrail",
    ):
        assert report[key] == expected[key], (key, report[key], expected[key])
    assert report["native_namespace_roundtrips"] == report["trial_count"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
