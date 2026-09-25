import json
from pathlib import Path

from sentinel_experiments.kubernetes import KubectlTransport, load_targets
from sentinel_experiments.readiness import check_kubernetes_readiness

ROOT = Path(__file__).parents[1]


class ReadinessRunner:
    def __init__(self, *, observer_patch: bool = False, unconverged: bool = False):
        self.observer_patch = observer_patch
        self.unconverged = unconverged
        self.commands = []

    def __call__(self, arguments):
        command = tuple(arguments)
        self.commands.append(command)
        context = command[2]
        if "auth" in command:
            verb = command[command.index("can-i") + 1]
            resource = command[command.index("can-i") + 2]
            if resource == "secrets":
                return "no\n"
            if context == "observer":
                allowed = verb == "get" or self.observer_patch
                return "yes\n" if allowed else "no\n"
            return "yes\n" if verb == "patch" else "no\n"

        name = command[command.index("deployment") + 1]
        namespace = command[command.index("--namespace") + 1]
        desired = 1
        available = 0 if self.unconverged and name == "adservice" else desired
        return json.dumps(
            {
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "generation": 2,
                    "resourceVersion": "11",
                },
                "spec": {"replicas": desired},
                "status": {
                    "availableReplicas": available,
                    "observedGeneration": 2,
                },
            }
        )


def targets():
    return load_targets(ROOT / "external/kubernetes_targets.json")


def test_readiness_proves_context_rbac_and_target_availability():
    runner = ReadinessRunner()
    report = check_kubernetes_readiness(
        KubectlTransport("observer", runner),
        KubectlTransport("actuator", runner),
        targets(),
    )
    assert report.ready
    assert len(report.checks) == 19
    assert len(report.to_dict()["digest"]) == 64
    assert any(
        command[3:7] == ("auth", "can-i", "patch", "deployments.apps/scale")
        and "--resource-name" in command
        for command in runner.commands
    )


def test_readiness_fails_closed_before_calls_for_shared_context():
    runner = ReadinessRunner()
    report = check_kubernetes_readiness(
        KubectlTransport("shared", runner),
        KubectlTransport("shared", runner),
        targets(),
    )
    assert not report.ready
    assert len(report.checks) == 1
    assert runner.commands == []


def test_readiness_rejects_observer_mutation_authority():
    report = check_kubernetes_readiness(
        KubectlTransport("observer", ReadinessRunner(observer_patch=True)),
        KubectlTransport("actuator", ReadinessRunner()),
        targets(),
    )
    assert not report.ready
    failed = {check.name for check in report.checks if not check.passed}
    assert "online-boutique:adservice:observer-no-patch" in failed


def test_readiness_rejects_unconverged_target():
    runner = ReadinessRunner(unconverged=True)
    report = check_kubernetes_readiness(
        KubectlTransport("observer", runner),
        KubectlTransport("actuator", runner),
        targets(),
    )
    assert not report.ready
    failed = {check.name for check in report.checks if not check.passed}
    assert "online-boutique:adservice:available" in failed


def test_rbac_manifest_is_target_scoped_and_contains_no_wildcards():
    manifest = json.loads(
        (ROOT / "deploy/kubernetes/experiment-rbac.json").read_text()
    )
    items = manifest["items"]
    namespaces = {
        item["metadata"]["name"] for item in items if item["kind"] == "Namespace"
    }
    assert namespaces == {"sentinel-online-boutique", "sentinel-otel-demo"}

    roles = [item for item in items if item["kind"] == "Role"]
    assert len(roles) == 4
    assert "*" not in json.dumps(roles)
    for role in roles:
        rule = role["rules"][0]
        assert rule["resourceNames"]
        assert "secrets" not in rule["resources"]
        if role["metadata"]["name"] == "sentinel-observer":
            assert rule["resources"] == ["deployments"]
            assert rule["verbs"] == ["get"]
        else:
            assert rule["resources"] == ["deployments/scale"]
            assert rule["verbs"] == ["get", "patch", "update"]
