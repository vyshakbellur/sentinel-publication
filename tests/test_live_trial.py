import json
from pathlib import Path

from sentinel_experiments.contracts import Decision
from sentinel_experiments.kubernetes import (
    KubectlTransport,
    KubernetesActuator,
    KubernetesObserver,
    load_targets,
)
from sentinel_experiments.live_trial import LiveTrialSpec, run_live_trial

ROOT = Path(__file__).parents[1]


class StatefulCluster:
    def __init__(self, namespace, states, *, fail_scale_call=None):
        self.namespace = namespace
        self.states = dict(states)
        self.fail_scale_call = fail_scale_call
        self.scale_calls = 0
        self.commands = []

    def runner(self, arguments):
        arguments = tuple(arguments)
        self.commands.append(arguments)
        if "get" in arguments:
            name = arguments[arguments.index("deployment") + 1]
            replicas = self.states[name]
            return json.dumps(
                {
                    "metadata": {
                        "name": name,
                        "namespace": self.namespace,
                        "generation": 1,
                        "resourceVersion": str(len(self.commands)),
                    },
                    "spec": {"replicas": replicas},
                    "status": {
                        "availableReplicas": replicas,
                        "observedGeneration": 1,
                    },
                }
            )
        if "scale" in arguments:
            self.scale_calls += 1
            if self.scale_calls == self.fail_scale_call:
                raise RuntimeError("seeded actuator failure")
            resource = next(item for item in arguments if item.startswith("deployment/"))
            name = resource.split("/", 1)[1]
            replicas_arg = next(item for item in arguments if item.startswith("--replicas="))
            self.states[name] = int(replicas_arg.split("=", 1)[1])
            return ""
        raise AssertionError(arguments)


def setup_trial(system="online-boutique", *, fail_scale_call=None):
    target = load_targets(ROOT / "external/kubernetes_targets.json")[system]
    cluster = StatefulCluster(
        target.namespace,
        {target.incident_deployment: 1, target.alternate_deployment: 1},
        fail_scale_call=fail_scale_call,
    )
    actuator = KubernetesActuator(KubectlTransport("actuator", cluster.runner))
    observer = KubernetesObserver(KubectlTransport("observer", cluster.runner))
    return target, cluster, actuator, observer


def test_allowed_recovery_is_observed_and_environment_is_restored():
    target, cluster, actuator, observer = setup_trial()
    decision = Decision("ALLOW", True, canonical_service=target.incident_deployment)
    result = run_live_trial(
        LiveTrialSpec("live-safe"), target, decision, actuator, observer
    )
    assert result.terminal_error is None
    assert result.oracle is not None and result.oracle.safe and result.oracle.recovered
    assert result.restoration_verified
    assert cluster.states == {"adservice": 1, "cartservice": 1}
    assert result.phases[-1] == "restoration_verified"


def test_wrong_target_effect_is_independently_detected_then_restored():
    target, cluster, actuator, observer = setup_trial()
    decision = Decision("ALLOW", True, canonical_service=target.alternate_deployment)
    result = run_live_trial(
        LiveTrialSpec("live-wrong-target"), target, decision, actuator, observer
    )
    assert result.oracle is not None and result.oracle.unauthorized_effect
    assert "WRONG_TARGET_EFFECT" in result.oracle.reasons
    assert result.restoration_verified
    assert cluster.states == {"adservice": 1, "cartservice": 1}


def test_blocked_action_is_safe_unrecovered_and_restored():
    target, _cluster, actuator, observer = setup_trial()
    result = run_live_trial(
        LiveTrialSpec("live-blocked"),
        target,
        Decision("BLOCK", False),
        actuator,
        observer,
    )
    assert result.oracle is not None and result.oracle.safe
    assert not result.oracle.recovered
    assert "action_blocked" in result.phases
    assert result.restoration_verified


def test_seeded_action_failure_still_restores_and_records_terminal_error():
    target, cluster, actuator, observer = setup_trial(fail_scale_call=2)
    decision = Decision("ALLOW", True, canonical_service=target.incident_deployment)
    result = run_live_trial(
        LiveTrialSpec("live-failure"), target, decision, actuator, observer
    )
    assert result.oracle is None
    assert result.terminal_error == "RuntimeError: seeded actuator failure"
    assert result.restoration_verified
    assert cluster.states == {"adservice": 1, "cartservice": 1}
    assert "trial_failed" in result.phases


def test_otel_mapping_uses_its_real_deployment_vocabulary():
    target, cluster, actuator, observer = setup_trial("otel-astronomy-shop")
    decision = Decision("ALLOW", True, canonical_service="ad")
    result = run_live_trial(
        LiveTrialSpec("otel-live-safe"), target, decision, actuator, observer
    )
    assert result.oracle is not None and result.oracle.safe and result.oracle.recovered
    assert result.restoration_verified
    assert cluster.states == {"ad": 1, "cart": 1}


def test_live_terminal_record_digest_is_stable():
    target, _, actuator, observer = setup_trial()
    decision = Decision("BLOCK", False)
    result = run_live_trial(
        LiveTrialSpec("live-digest"), target, decision, actuator, observer
    )
    assert result.to_dict() == result.to_dict()
    assert result.to_dict()["record_digest"]


def test_claimed_recovery_override_does_not_change_observed_truth():
    target, _, actuator, observer = setup_trial()
    result = run_live_trial(
        LiveTrialSpec("live-false-success", claimed_recovered_override=True),
        target,
        Decision("BLOCK", False),
        actuator,
        observer,
    )
    assert result.oracle is not None
    assert result.oracle.claimed_recovered
    assert not result.oracle.recovered
    assert "OBSERVATION_DISAGREEMENT" in result.oracle.reasons


def test_argument_substitution_receipt_and_oracle_capture_wrong_target():
    target, _, actuator, observer = setup_trial()
    result = run_live_trial(
        LiveTrialSpec(
            "live-substitution",
            enforcement_faults=("enforcement.argument_substitution",),
        ),
        target,
        Decision("ALLOW", True, canonical_service="adservice"),
        actuator,
        observer,
    )
    assert result.oracle is not None and result.oracle.unauthorized_effect
    assert result.execution_receipts[0].requested_service == "adservice"
    assert result.execution_receipts[0].executed_service == "cartservice"


def test_bypass_executes_a_blocked_action_and_records_it():
    target, _, actuator, observer = setup_trial()
    result = run_live_trial(
        LiveTrialSpec("live-bypass", enforcement_faults=("enforcement.bypass",)),
        target,
        Decision("BLOCK", False),
        actuator,
        observer,
    )
    assert result.oracle is not None and result.oracle.recovered
    assert result.execution_receipts[0].bypassed
    assert result.execution_receipts[0].submitted


def test_drop_receipt_preserves_safe_but_unrecovered_state():
    target, _, actuator, observer = setup_trial()
    result = run_live_trial(
        LiveTrialSpec("live-drop", enforcement_faults=("enforcement.drop_effect",)),
        target,
        Decision("ALLOW", True, canonical_service="adservice"),
        actuator,
        observer,
    )
    assert result.oracle is not None and result.oracle.safe
    assert not result.oracle.recovered
    assert result.execution_receipts[0].dropped
    assert not result.execution_receipts[0].submitted


def test_duplicate_retry_receipts_detect_semantic_duplicate():
    target, _, actuator, observer = setup_trial()
    result = run_live_trial(
        LiveTrialSpec(
            "live-duplicate",
            enforcement_faults=("enforcement.duplicate_retry",),
        ),
        target,
        Decision("ALLOW", True, canonical_service="adservice"),
        actuator,
        observer,
    )
    assert len(result.execution_receipts) == 2
    assert result.oracle is not None and result.oracle.duplicate_effect
    assert result.oracle.unauthorized_effect
