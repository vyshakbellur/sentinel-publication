"""Run the hash-bound iteration-28 final publication audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sentinel_experiments.final_audit import build_report


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repository.resolve()
    content = args.protocol.read_bytes()
    protocol = json.loads(content)
    reports = {}
    for name, spec in protocol["source_reports"].items():
        path = root / spec["path"]
        actual = _sha256(path)
        if actual != spec["sha256"]:
            raise SystemExit(f"evidence hash mismatch for {name}: {actual}")
        reports[name] = json.loads(path.read_text())
    report = build_report(protocol, reports, hashlib.sha256(content).hexdigest())
    if not report["accepted"]:
        raise SystemExit("final audit acceptance failed")
    if report["extracted_evidence"]["publication_ready"]:
        raise SystemExit("unsupported publication-ready verdict")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
