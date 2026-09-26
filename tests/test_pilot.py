import json
from pathlib import Path

import pytest

from sentinel_experiments.kubernetes import KubectlTransport, load_targets
from sentinel_experiments.pilot import (
    PilotSpec,
    run_live_pilot,
    write_pilot_record,
)
from sentinel_experiments.study_execution import StudyAssignment

ROOT = Path(__file__).parents[1]


class PilotCluster:
    def __init__(self, namespace, names, *, observer_patch=False, fail_get_after=None):
        self.namespace = namespace
        self.states = {name: 1 for name in names}
        self.observer_patch = observer_patch
        self.fail_get_after = fail_get_after
        self.get_calls = 0
        self.scale_calls = 0
        self.commands = []

    def runner(self, arguments):
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
            else:
                allowed = verb == "patch"
            return "yes\n" if allowed else "no\n"
        if "get" in command:
            self.get_calls += 1
            if self.get_calls > (self.fail_get_after or 10**6):
                raise RuntimeError("seeded observation failure")
            name = command[command.index("deployment") + 1]
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
        if "scale" in command:
            self.scale_calls += 1
            resource = next(value for value in command if value.startswith("deployment/"))
            name = resource.split("/", 1)[1]
            replicas = next(value for value in command if value.startswith("--replicas="))
            self.states[name] = int(replicas.split("=", 1)[1])
            return ""
        raise AssertionError(command)


def setup(*, observer_patch=False, fail_get_after=None):
    targets = load_targets(ROOT / "external/kubernetes_targets.json")
    target = targets["online-boutique"]
    cluster = PilotCluster(
        target.namespace,
        (target.incident_deployment, target.alternate_deployment),
        observer_patch=observer_patch,
        fail_get_after=fail_get_after,
    )
    protocol = json.loads(
        (ROOT / "experiments/protocol/confirmatory_protocol.json").read_text()
    )
    return targets, cluster, protocol


def run(spec, targets, cluster, protocol, *, shared_context=False):
    observer_context = "shared" if shared_context else "observer"
    actuator_context = "shared" if shared_context else "actuator"
    return run_live_pilot(
        spec,
        protocol,
        json.loads(
            (ROOT / "experiments/protocol/pairwise_design.json").read_text()
        ),
        json.loads(
            (ROOT / "experiments/protocol/study_partition.json").read_text()
        ),
        targets,
        KubectlTransport(observer_context, cluster.runner),
        KubectlTransport(actuator_context, cluster.runner),
    )


def pilot_spec(suffix, guardrail):
    return PilotSpec(
        f"PILOT-{suffix}",
        "online-boutique",
        guardrail,
        StudyAssignment("pilot", "PW000", "deploy-1", "replicas-zero", "seed-1"),
    )


def test_one_row_pilot_binds_decision_runs_trial_and_restores():
    targets, cluster, protocol = setup()
    result = run(
        pilot_spec("001", "none"),
        targets,
        cluster,
        protocol,
    )
    assert result.succeeded
    assert result.readiness is not None and result.readiness.ready
    assert result.decision is not None and result.decision.allowed
    assert result.trial is not None and result.trial.oracle is not None
    assert result.trial.oracle.safe and result.trial.oracle.recovered
    assert result.trial.restoration_verified
    assert cluster.states == {"adservice": 1, "cartservice": 1}


def test_failed_readiness_never_mutates_cluster():
    targets, cluster, protocol = setup()
    result = run(
        pilot_spec("shared", "guardian"),
        targets,
        cluster,
        protocol,
        shared_context=True,
    )
    assert not result.succeeded and result.terminal_stage == "readiness"
    assert result.study is not None and result.study.phase == "pilot"
    assert cluster.commands == []
    assert cluster.scale_calls == 0


def test_precapture_failure_becomes_terminal_record_without_mutation():
    targets, cluster, protocol = setup(fail_get_after=2)
    result = run(
        pilot_spec("observation-failure", "always_deny"),
        targets,
        cluster,
        protocol,
    )
    assert not result.succeeded and result.terminal_stage == "trial"
    assert "seeded observation failure" in (result.terminal_error or "")
    assert result.decision is not None and not result.decision.allowed
    assert cluster.scale_calls == 0


def test_non_frozen_condition_is_rejected_before_cluster_calls():
    targets, cluster, protocol = setup()
    result = run(
        pilot_spec("unknown", "new_guardrail"),
        targets,
        cluster,
        protocol,
    )
    assert not result.succeeded and result.terminal_stage == "protocol"
    assert cluster.commands == []


def test_unimplemented_fault_row_is_rejected_before_cluster_calls():
    targets, cluster, protocol = setup()
    spec = PilotSpec(
        "PILOT-fault-row",
        "online-boutique",
        "guardian",
        StudyAssignment("pilot", "PW001", "deploy-1", "replicas-zero", "seed-1"),
    )
    result = run(spec, targets, cluster, protocol)
    assert not result.succeeded and result.terminal_stage == "study"
    assert "fault adapter" in (result.terminal_error or "")
    assert cluster.commands == []


def test_pilot_record_is_content_digested_and_cannot_be_overwritten(tmp_path):
    targets, cluster, protocol = setup()
    result = run(
        pilot_spec("record", "always_deny"),
        targets,
        cluster,
        protocol,
    )
    output = tmp_path / "pilot-record.json"
    write_pilot_record(output, result)
    payload = json.loads(output.read_text())
    assert payload["schema_version"] == "sentinel.live-pilot.v2"
    assert len(payload["record_digest"]) == 64
    assert payload["spec"]["trial_id"] == "PILOT-record"
    assert payload["study"]["phase"] == "pilot"
    assert not payload["study"]["confirmatory_eligible"]
    with pytest.raises(FileExistsError):
        write_pilot_record(output, result)
