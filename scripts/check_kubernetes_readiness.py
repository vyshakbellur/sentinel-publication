"""Emit a machine-readable Kubernetes pilot readiness report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinel_experiments.kubernetes import KubectlTransport, load_targets
from sentinel_experiments.readiness import check_kubernetes_readiness


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observer-context", required=True)
    parser.add_argument("--actuator-context", required=True)
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path("external/kubernetes_targets.json"),
    )
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()

    report = check_kubernetes_readiness(
        KubectlTransport(arguments.observer_context),
        KubectlTransport(arguments.actuator_context),
        load_targets(arguments.targets),
    )
    rendered = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
