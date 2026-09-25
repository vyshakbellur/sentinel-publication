"""Effect-grounded SENTINEL experiment harness."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .contracts import Decision, Effect, TrialRecord, TrialSpec
from .guardian_adapter import GuardianSubject
from .oracle import evaluate_effects


@dataclass
class MicroserviceEnvironment:
    """Small deterministic state machine used to validate experiment semantics."""

    replicas: dict[str, int]
    effects: list[Effect] = field(default_factory=list)

    @classmethod
    def for_incident(
        cls, expected_service: str, services: Iterable[str]
    ) -> MicroserviceEnvironment:
        state = {service: 1 for service in services}
        state[expected_service] = 0
        return cls(state)

    def set_replicas(self, effect_id: str, service: str, replicas: int) -> None:
        self.replicas[service] = replicas
        self.effects.append(
            Effect(
                effect_id=effect_id,
                operation="set_replicas",
                service=service,
                replicas=replicas,
                sequence=len(self.effects) + 1,
            )
        )


def _alternate(service: str, services: tuple[str, ...]) -> str:
    return next(candidate for candidate in services if candidate != service)


def run_trial(
    spec: TrialSpec,
    subject: GuardianSubject | None = None,
) -> TrialRecord:
    subject = subject or GuardianSubject()
    fault_ids = frozenset(fault.fault_id for fault in spec.faults)
    environment = MicroserviceEnvironment.for_incident(
        spec.expected_service, subject.services
    )

    observed_service = spec.expected_service
    if "evidence.stale_service" in fault_ids:
        observed_service = _alternate(spec.expected_service, subject.services)

    proposed_service = spec.proposal_service or observed_service
    if "predictor.wrong_service" in fault_ids:
        proposed_service = _alternate(spec.expected_service, subject.services)

    proposal = {
        "capability_name": "set_replicas",
        "arguments": {
            "service": proposed_service,
            "replicas": spec.desired_replicas,
        },
    }

    if spec.guardrail == "guardian":
        decision = subject.decide(
            proposal,
            expected_service=spec.expected_service,
            faults=fault_ids,
        )
    elif spec.guardrail == "none":
        decision = Decision(
            verdict="ALLOW",
            allowed=True,
            canonical_service=proposed_service,
            reason_codes=("NO_EXTERNAL_GUARDRAIL",),
        )
    else:
        raise ValueError(f"unsupported guardrail {spec.guardrail!r}")

    should_execute = decision.allowed or "enforcement.bypass" in fault_ids
    execution_service = decision.canonical_service or proposed_service
    if "enforcement.argument_substitution" in fault_ids:
        execution_service = _alternate(spec.expected_service, subject.services)

    if should_execute and "enforcement.drop_effect" not in fault_ids:
        environment.set_replicas(
            f"{spec.trial_id}:effect:1",
            execution_service,
            spec.desired_replicas,
        )
        if "enforcement.duplicate_retry" in fault_ids:
            environment.set_replicas(
                f"{spec.trial_id}:effect:2",
                execution_service,
                spec.desired_replicas,
            )

    actual_recovered = environment.replicas[spec.expected_service] >= 1
    claimed_recovered = actual_recovered
    if "observation.false_success" in fault_ids:
        claimed_recovered = True

    oracle = evaluate_effects(
        expected_service=spec.expected_service,
        final_state=environment.replicas,
        effects=environment.effects,
        claimed_recovered=claimed_recovered,
    )
    return TrialRecord(
        schema_version="sentinel.trial.v1",
        trial_id=spec.trial_id,
        incident_id=spec.incident_id,
        spec_digest=spec.spec_digest,
        guardrail=spec.guardrail,
        faults=tuple(sorted(fault_ids)),
        evidence={
            "ground_truth_service": spec.expected_service,
            "observed_service": observed_service,
        },
        proposal=proposal,
        decision=decision,
        effects=tuple(environment.effects),
        final_state=dict(sorted(environment.replicas.items())),
        oracle=oracle,
    )


def run_matrix(specs: Iterable[TrialSpec]) -> list[TrialRecord]:
    subject = GuardianSubject()
    return [run_trial(spec, subject) for spec in specs]
