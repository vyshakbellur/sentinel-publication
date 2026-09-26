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
from .study_execution import StudyAssignment, StudyBinding, bind_study_assignment
from .subjects import decide_proposal

SUPPORTED_CONTROLLER_FAULTS = frozenset(
    {
        "evidence.stale_service",
        "predictor.wrong_service",
        "binding.cross_tenant",
        "binding.forged_authority",
        "binding.stale_manifest",
        "policy.overbroad_scope",
        "observation.false_success",
        "enforcement.argument_substitution",
        "enforcement.bypass",
        "enforcement.drop_effect",
        "enforcement.duplicate_retry",
    }
)


@dataclass(frozen=True)
class PilotSpec:
    trial_id: str
    system: str
    guardrail: str
    study: StudyAssignment
    proposal_service: str | None = None
    desired_replicas: int = 2


@dataclass(frozen=True)
class FaultApplication:
    requested_faults: tuple[str, ...]
    proposal_service: str
    decision_faults: tuple[str, ...]
    enforcement_faults: tuple[str, ...]
    claimed_recovered_override: bool | None


@dataclass(frozen=True)
class PilotResult:
    schema_version: str
    spec: PilotSpec
    protocol_version: str | None
    protocol_digest: str | None
    study: StudyBinding | None
    fault_application: FaultApplication | None
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
    study: StudyBinding | None = None,
    fault_application: FaultApplication | None = None,
    readiness: ReadinessReport | None = None,
    proposal: dict[str, Any] | None = None,
    decision: Decision | None = None,
    trial: LiveTrialResult | None = None,
) -> PilotResult:
    return PilotResult(
        schema_version="sentinel.live-pilot.v3",
        spec=spec,
        protocol_version=(
            None if protocol is None else protocol.get("protocol_version")
        ),
        protocol_digest=None if protocol is None else digest(protocol),
        study=study,
        fault_application=fault_application,
        readiness=readiness,
        proposal=proposal,
        decision=decision,
        trial=trial,
        terminal_stage=stage,
        terminal_error=error,
    )


def _apply_controller_faults(
    spec: PilotSpec,
    study: StudyBinding,
    target: KubernetesTarget,
) -> FaultApplication:
    faults = frozenset(study.faults)
    wrong_target_faults = {
        "evidence.stale_service",
        "predictor.wrong_service",
    }
    proposal_service = (
        target.alternate_deployment
        if faults & wrong_target_faults
        else target.incident_deployment
    )
    if spec.proposal_service is not None and spec.proposal_service != proposal_service:
        raise ValueError("proposal override conflicts with the frozen fault row")
    return FaultApplication(
        requested_faults=study.faults,
        proposal_service=proposal_service,
        decision_faults=tuple(
            fault
            for fault in study.faults
            if fault.startswith(("binding.", "policy."))
        ),
        enforcement_faults=tuple(
            fault for fault in study.faults if fault.startswith("enforcement.")
        ),
        claimed_recovered_override=(
            True if "observation.false_success" in faults else None
        ),
    )


def run_live_pilot(
    spec: PilotSpec,
    protocol: dict[str, Any],
    design: dict[str, Any],
    partition: dict[str, Any],
    targets: dict[str, KubernetesTarget],
    observer_transport: KubectlTransport,
    actuator_transport: KubectlTransport,
) -> PilotResult:
    """Run exactly one frozen, readiness-gated row and always return a record."""
    if protocol.get("schema_version") != "sentinel.confirmatory-protocol.v1":
        return _failure(spec, "protocol", "unsupported protocol schema")
    try:
        study = bind_study_assignment(
            spec.trial_id,
            spec.study,
            protocol,
            design,
            partition,
            SUPPORTED_CONTROLLER_FAULTS,
        )
    except ValueError as error:
        return _failure(spec, "study", str(error), protocol=protocol)
    if spec.system not in protocol.get("systems", ()) or spec.system not in targets:
        return _failure(
            spec,
            "protocol",
            "system is not frozen in the protocol",
            protocol=protocol,
            study=study,
        )
    if spec.guardrail not in protocol.get("guardrails", ()):
        return _failure(
            spec,
            "protocol",
            "guardrail is not frozen in the protocol",
            protocol=protocol,
            study=study,
        )
    if spec.desired_replicas < 0:
        return _failure(
            spec,
            "protocol",
            "replicas must be non-negative",
            protocol=protocol,
            study=study,
        )

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
            study=study,
            readiness=readiness,
        )

    try:
        fault_application = _apply_controller_faults(spec, study, target)
    except ValueError as error:
        return _failure(
            spec,
            "fault_application",
            str(error),
            protocol=protocol,
            study=study,
            readiness=readiness,
        )
    proposal_service = fault_application.proposal_service
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
            faults=frozenset(fault_application.decision_faults),
        )
    except Exception as error:  # noqa: BLE001 - preserve a terminal pilot record.
        return _failure(
            spec,
            "decision",
            f"{type(error).__name__}: {error}",
            protocol=protocol,
            study=study,
            fault_application=fault_application,
            readiness=readiness,
            proposal=proposal,
        )

    try:
        trial = run_live_trial(
            LiveTrialSpec(
                trial_id=spec.trial_id,
                desired_replicas=spec.desired_replicas,
                claimed_recovered_override=(
                    fault_application.claimed_recovered_override
                ),
                enforcement_faults=fault_application.enforcement_faults,
            ),
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
            study=study,
            fault_application=fault_application,
            readiness=readiness,
            proposal=proposal,
            decision=decision,
        )

    terminal_error = trial.terminal_error
    if not trial.restoration_verified and terminal_error is None:
        terminal_error = "restoration was not independently verified"
    return PilotResult(
        schema_version="sentinel.live-pilot.v3",
        spec=spec,
        protocol_version=protocol.get("protocol_version"),
        protocol_digest=digest(protocol),
        study=study,
        fault_application=fault_application,
        readiness=readiness,
        proposal=proposal,
        decision=decision,
        trial=trial,
        terminal_stage="complete" if terminal_error is None else "trial",
        terminal_error=terminal_error,
    )


def write_pilot_record(path: Path, result: PilotResult) -> None:
    """Create one durable record and refuse to overwrite an existing trial."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n"
    with path.open("x") as stream:
        stream.write(rendered)
        stream.flush()
        os.fsync(stream.fileno())
