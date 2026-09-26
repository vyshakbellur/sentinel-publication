"""Run one readiness-gated SENTINEL Kubernetes pilot row."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .kubernetes import KubectlTransport, load_targets
from .pilot import PilotSpec, run_live_pilot, write_pilot_record
from .study_execution import StudyAssignment

ROOT = Path(__file__).parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--system", required=True)
    parser.add_argument("--guardrail", required=True)
    parser.add_argument(
        "--phase",
        choices=("pilot", "fault_surface_census", "confirmatory"),
        required=True,
    )
    parser.add_argument("--design-row-id", required=True)
    parser.add_argument("--deployment-instance-id", required=True)
    parser.add_argument("--incident-template-id", required=True)
    parser.add_argument("--load-seed", required=True)
    parser.add_argument("--observer-context", required=True)
    parser.add_argument("--actuator-context", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--proposal-service")
    parser.add_argument("--desired-replicas", type=int, default=2)
    parser.add_argument(
        "--protocol",
        type=Path,
        default=ROOT / "experiments/protocol/confirmatory_protocol.json",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=ROOT / "external/kubernetes_targets.json",
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=ROOT / "experiments/protocol/pairwise_design.json",
    )
    parser.add_argument(
        "--partition",
        type=Path,
        default=ROOT / "experiments/protocol/study_partition.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    protocol = json.loads(arguments.protocol.read_text())
    design = json.loads(arguments.design.read_text())
    partition = json.loads(arguments.partition.read_text())
    result = run_live_pilot(
        PilotSpec(
            arguments.trial_id,
            arguments.system,
            arguments.guardrail,
            StudyAssignment(
                arguments.phase,
                arguments.design_row_id,
                arguments.deployment_instance_id,
                arguments.incident_template_id,
                arguments.load_seed,
            ),
            arguments.proposal_service,
            arguments.desired_replicas,
        ),
        protocol,
        design,
        partition,
        load_targets(arguments.targets),
        KubectlTransport(arguments.observer_context),
        KubectlTransport(arguments.actuator_context),
    )
    write_pilot_record(arguments.output, result)
    print(json.dumps({"output": str(arguments.output), "succeeded": result.succeeded}))
    return 0 if result.succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
