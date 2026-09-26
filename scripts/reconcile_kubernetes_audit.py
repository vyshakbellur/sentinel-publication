"""Reconcile one live-pilot record with bounded Kubernetes audit JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinel_experiments.kubernetes_audit import (
    parse_kubernetes_audit_write,
    reconcile_pilot_record,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-record", type=Path, required=True)
    parser.add_argument("--audit-jsonl", type=Path, required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.pilot_record.read_text())
    events = tuple(
        parse_kubernetes_audit_write(line)
        for line in args.audit_jsonl.read_text().splitlines()
        if line.strip()
    )
    report = reconcile_pilot_record(
        record,
        events,
        expected_namespace=args.namespace,
        expected_username=args.username,
    )
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(report["reconciliation"], indent=2, sort_keys=True))
    return 0 if report["reconciliation"]["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
