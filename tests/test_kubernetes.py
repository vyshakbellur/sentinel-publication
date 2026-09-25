import json
from pathlib import Path

import pytest

from sentinel_experiments.kubernetes import (
    KubectlTransport,
    KubernetesActuator,
    KubernetesObserver,
    ResetContract,
    load_targets,
    parse_deployment,
)

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests/fixtures/kubernetes"


class RecordedRunner:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.commands = []

    def __call__(self, arguments):
        self.commands.append(tuple(arguments))
        return next(self.responses)


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


def test_recorded_workload_states_parse_and_converge():
    online = parse_deployment(fixture("online_boutique_adservice.json"))
    otel = parse_deployment(fixture("otel_ad.json"))
    assert online.name == "adservice" and online.desired_replicas == 2
    assert otel.name == "ad" and otel.available_replicas == 1
    assert online.converged and otel.converged


def test_observer_uses_its_own_context_and_read_only_command():
    runner = RecordedRunner([fixture("online_boutique_adservice.json")])
    observer = KubernetesObserver(KubectlTransport("observer-context", runner))
    state = observer.deployment("sentinel-online-boutique", "adservice")
    assert state.converged
    assert runner.commands == [
        (
            "kubectl",
            "--context",
            "observer-context",
            "--namespace",
            "sentinel-online-boutique",
            "get",
            "deployment",
            "adservice",
            "--output=json",
        )
    ]


def test_actuator_uses_separate_context_and_validates_replicas():
    runner = RecordedRunner([""])
    actuator = KubernetesActuator(KubectlTransport("actuator-context", runner))
    actuator.set_replicas("sentinel-online-boutique", "adservice", 0)
    assert "scale" in runner.commands[0]
    assert "--replicas=0" in runner.commands[0]
    with pytest.raises(ValueError, match="non-negative"):
        actuator.set_replicas("namespace", "deployment", -1)


def test_reset_contract_restores_sorted_targets_and_verifies_fresh_state():
    actuator_runner = RecordedRunner(["", ""])
    actuator = KubernetesActuator(KubectlTransport("actuator", actuator_runner))
    contract = ResetContract(
        "sentinel-online-boutique",
        {"cartservice": 1, "adservice": 2},
    )
    contract.restore(actuator)
    assert "deployment/adservice" in actuator_runner.commands[0]
    assert "deployment/cartservice" in actuator_runner.commands[1]

    ad = json.loads(fixture("online_boutique_adservice.json"))
    cart = json.loads(fixture("online_boutique_adservice.json"))
    cart["metadata"]["name"] = "cartservice"
    cart["spec"]["replicas"] = 1
    cart["status"]["availableReplicas"] = 1
    observer_runner = RecordedRunner([json.dumps(cart), json.dumps(ad)])
    observer = KubernetesObserver(KubectlTransport("observer", observer_runner))
    assert contract.verify(observer)


def test_target_mapping_matches_locked_workload_revisions():
    targets = load_targets(ROOT / "external/kubernetes_targets.json")
    lock = json.loads((ROOT / "external/workloads.lock.json").read_text())
    revisions = {item["id"]: item["revision"] for item in lock["workloads"]}
    assert set(targets) == {"online-boutique", "otel-astronomy-shop"}
    for target in targets.values():
        source = target.deployment_source
        assert revisions[source["workload_id"]] == source["revision"]
