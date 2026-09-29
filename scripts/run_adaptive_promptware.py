"""Run frozen deterministic adaptive development search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sentinel_experiments.adaptive_promptware import build_report


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repository.resolve()
    content = args.protocol.read_bytes()
    protocol = json.loads(content)
    for name, spec in protocol["source_reports"].items():
        actual = _sha256(root / spec["path"])
        assert actual == spec["sha256"], (name, actual, spec["sha256"])
    report = build_report(protocol, hashlib.sha256(content).hexdigest())
    for key, expected in protocol["acceptance"].items():
        assert report[key] == expected, (key, report[key], expected)
    assert report["native_namespace_roundtrips"] == report["candidate_trial_count"]
    assert report["confirmatory_holdouts_evaluated"] == 0
    assert report["trusted_boundary_faults_injected"] == 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
