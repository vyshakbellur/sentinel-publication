"""Fail-safe state machine for one bounded live Kubernetes trial."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .contracts import Decision, Effect, OracleResult, digest
from .kubernetes import (
    DeploymentState,
    KubernetesActuator,
    KubernetesObserver,
    KubernetesTarget,
    ResetContract,
)
from .oracle import evaluate_effects


@dataclass(frozen=True)
class LiveTrialSpec:
    trial_id: str
    desired_replicas: int = 2
    effect_id: str = "remediation-1"
    claimed_recovered_override: bool | None = None


@dataclass(frozen=True)
class LiveTrialResult:
    schema_version: str
    trial_id: str
    system: str
    phases: tuple[str, ...]
    decision: Decision
    effects: tuple[Effect, ...]
    oracle: OracleResult | None
    restoration_verified: bool
    terminal_error: str | None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["record_digest"] = digest(value)
        return value


def _snapshot(
    observer: KubernetesObserver, target: KubernetesTarget
) -> dict[str, DeploymentState]:
    return {
        name: observer.deployment(target.namespace, name)
        for name in (target.incident_deployment, target.alternate_deployment)
    }


def _observed_effects(
    before: dict[str, DeploymentState],
    after: dict[str, DeploymentState],
    effect_id: str,
) -> tuple[Effect, ...]:
    effects: list[Effect] = []
    for name in sorted(before):
        if after[name].desired_replicas == before[name].desired_replicas:
            continue
        effects.append(
            Effect(
                effect_id=f"{effect_id}:{name}",
                operation="set_replicas",
                service=name,
                replicas=after[name].desired_replicas,
                sequence=len(effects) + 1,
                completed=after[name].converged,
            )
        )
    return tuple(effects)


def run_live_trial(
    spec: LiveTrialSpec,
    target: KubernetesTarget,
    decision: Decision,
    actuator: KubernetesActuator,
    observer: KubernetesObserver,
) -> LiveTrialResult:
    """Run one trial and attempt restoration after every post-capture failure."""
    phases: list[str] = []
    effects: tuple[Effect, ...] = ()
    oracle: OracleResult | None = None
    terminal_error: str | None = None
    restoration_verified = False
    reset = ResetContract.capture(observer, target)
    phases.append("pre_state_captured")
    try:
        actuator.set_replicas(target.namespace, target.incident_deployment, 0)
        incident_state = _snapshot(observer, target)
        if incident_state[target.incident_deployment].desired_replicas != 0:
            raise RuntimeError("incident injection was not independently observed")
        phases.append("incident_observed")

        if decision.allowed:
            action_service = decision.canonical_service or target.incident_deployment
            if action_service not in incident_state:
                raise RuntimeError("decision names a deployment outside the target map")
            actuator.set_replicas(
                target.namespace,
                action_service,
                spec.desired_replicas,
            )
            phases.append("action_submitted")
        else:
            phases.append("action_blocked")

        post_state = _snapshot(observer, target)
        phases.append("post_state_observed")
        effects = _observed_effects(incident_state, post_state, spec.effect_id)
        claimed_recovered = (
            decision.allowed
            if spec.claimed_recovered_override is None
            else spec.claimed_recovered_override
        )
        oracle = evaluate_effects(
            expected_service=target.incident_deployment,
            pre_state={
                name: state.desired_replicas for name, state in incident_state.items()
            },
            final_state={
                name: state.desired_replicas for name, state in post_state.items()
            },
            effects=effects,
            claimed_recovered=claimed_recovered,
        )
        phases.append("oracle_evaluated")
    except Exception as exc:  # noqa: BLE001 - terminal failures still restore.
        terminal_error = f"{type(exc).__name__}: {exc}"
        phases.append("trial_failed")
    finally:
        try:
            reset.restore(actuator)
            restoration_verified = reset.verify(observer)
            phases.append(
                "restoration_verified"
                if restoration_verified
                else "restoration_failed"
            )
        except Exception as exc:  # noqa: BLE001 - restoration failure is evidence.
            restoration_verified = False
            phases.append("restoration_failed")
            restoration_error = f"{type(exc).__name__}: {exc}"
            terminal_error = (
                restoration_error
                if terminal_error is None
                else f"{terminal_error}; restoration={restoration_error}"
            )

    return LiveTrialResult(
        schema_version="sentinel.live-trial.v1",
        trial_id=spec.trial_id,
        system=target.system,
        phases=tuple(phases),
        decision=decision,
        effects=effects,
        oracle=oracle,
        restoration_verified=restoration_verified,
        terminal_error=terminal_error,
    )
