"""One-row, readiness-gated live pilot orchestration."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .contracts import Decision, digest
from .kubernetes import (
    KubectlTransport,
    KubernetesActuator,
    KubernetesObserver,
    KubernetesTarget,
)
from .live_trial import LiveTrialResult, LiveTrialSpec, run_live_trial
from .readiness import ReadinessReport, check_kubernetes_readiness
from .subjects import decide_proposal


@dataclass(frozen=True)
class PilotSpec:
    trial_id: str
    system: str
    guardrail: str
    proposal_service: str | None = None
    desired_replicas: int = 2


@dataclass(frozen=True)
class PilotResult:
    schema_version: str
    spec: PilotSpec
    protocol_version: str | None
    protocol_digest: str | None
    readiness: ReadinessReport | None
    proposal: dict[str, Any] | None
    decision: Decision | None
    trial: LiveTrialResult | None
    terminal_stage: str
    terminal_error: str | None

    @property
    def succeeded(self) -> bool:
        return (
            self.terminal_error is None
            and self.trial is not None
            and self.trial.terminal_error is None
            and self.trial.restoration_verified
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["succeeded"] = self.succeeded
        value["record_digest"] = digest(value)
        return value


def _failure(
    spec: PilotSpec,
    stage: str,
    error: str,
    *,
    protocol: dict[str, Any] | None = None,
    readiness: ReadinessReport | None = None,
    proposal: dict[str, Any] | None = None,
    decision: Decision | None = None,
    trial: LiveTrialResult | None = None,
) -> PilotResult:
    return PilotResult(
        "sentinel.live-pilot.v1",
        spec,
        None if protocol is None else protocol.get("protocol_version"),
        None if protocol is None else digest(protocol),
        readiness,
        proposal,
        decision,
        trial,
        stage,
        error,
    )


def run_live_pilot(
    spec: PilotSpec,
    protocol: dict[str, Any],
    targets: dict[str, KubernetesTarget],
    observer_transport: KubectlTransport,
    actuator_transport: KubectlTransport,
) -> PilotResult:
    """Run exactly one frozen, readiness-gated row and always return a record."""
    if protocol.get("schema_version") != "sentinel.confirmatory-protocol.v1":
        return _failure(spec, "protocol", "unsupported protocol schema")
    if spec.system not in protocol.get("systems", ()) or spec.system not in targets:
        return _failure(spec, "protocol", "system is not frozen in the protocol", protocol=protocol)
    if spec.guardrail not in protocol.get("guardrails", ()):
        return _failure(
            spec,
            "protocol",
            "guardrail is not frozen in the protocol",
            protocol=protocol,
        )
    if spec.desired_replicas < 0:
        return _failure(spec, "protocol", "replicas must be non-negative", protocol=protocol)

    target = targets[spec.system]
    readiness = check_kubernetes_readiness(
        observer_transport,
        actuator_transport,
        {spec.system: target},
    )
    if not readiness.ready:
        return _failure(
            spec,
            "readiness",
            "Kubernetes readiness gate failed",
            protocol=protocol,
            readiness=readiness,
        )

    proposal_service = spec.proposal_service or target.incident_deployment
    proposal = {
        "capability_name": "set_replicas",
        "arguments": {
            "service": proposal_service,
            "replicas": spec.desired_replicas,
        },
    }
    try:
        decision = decide_proposal(
            spec.guardrail,
            proposal,
            expected_service=target.incident_deployment,
            services=(target.incident_deployment, target.alternate_deployment),
        )
    except Exception as error:  # noqa: BLE001 - preserve a terminal pilot record.
        return _failure(
            spec,
            "decision",
            f"{type(error).__name__}: {error}",
            protocol=protocol,
            readiness=readiness,
            proposal=proposal,
        )

    try:
        trial = run_live_trial(
            LiveTrialSpec(spec.trial_id, spec.desired_replicas),
            target,
            decision,
            KubernetesActuator(actuator_transport),
            KubernetesObserver(observer_transport),
        )
    except Exception as error:  # noqa: BLE001 - includes pre-capture failures.
        return _failure(
            spec,
            "trial",
            f"{type(error).__name__}: {error}",
            protocol=protocol,
            readiness=readiness,
            proposal=proposal,
            decision=decision,
        )

    terminal_error = trial.terminal_error
    if not trial.restoration_verified and terminal_error is None:
        terminal_error = "restoration was not independently verified"
    return PilotResult(
        "sentinel.live-pilot.v1",
        spec,
        protocol.get("protocol_version"),
        digest(protocol),
        readiness,
        proposal,
        decision,
        trial,
        "complete" if terminal_error is None else "trial",
        terminal_error,
    )


def write_pilot_record(path: Path, result: PilotResult) -> None:
    """Create one durable record and refuse to overwrite an existing trial."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n"
    with path.open("x") as stream:
        stream.write(rendered)
        stream.flush()
        os.fsync(stream.fileno())
