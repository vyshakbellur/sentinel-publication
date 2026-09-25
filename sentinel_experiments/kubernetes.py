"""Kubernetes actuation, independent observation, and reset contracts."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CommandRunner = Callable[[Sequence[str]], str]


def _subprocess_runner(arguments: Sequence[str]) -> str:
    return subprocess.run(
        list(arguments),
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout


@dataclass(frozen=True)
class KubernetesTarget:
    system: str
    namespace: str
    incident_deployment: str
    alternate_deployment: str
    deployment_source: Mapping[str, str]


@dataclass(frozen=True)
class DeploymentState:
    name: str
    namespace: str
    desired_replicas: int
    available_replicas: int
    generation: int
    observed_generation: int
    resource_version: str

    @property
    def converged(self) -> bool:
        return (
            self.desired_replicas == self.available_replicas
            and self.observed_generation >= self.generation
        )


def load_targets(path: Path) -> dict[str, KubernetesTarget]:
    payload = json.loads(path.read_text())
    if payload["schema_version"] != "sentinel.kubernetes-targets.v1":
        raise ValueError("unsupported Kubernetes target schema")
    targets = {
        item["system"]: KubernetesTarget(**item) for item in payload["targets"]
    }
    if len(targets) != len(payload["targets"]):
        raise ValueError("duplicate Kubernetes system mapping")
    return targets


def parse_deployment(payload: str) -> DeploymentState:
    value: dict[str, Any] = json.loads(payload)
    metadata = value["metadata"]
    specification = value["spec"]
    status = value.get("status", {})
    return DeploymentState(
        name=metadata["name"],
        namespace=metadata["namespace"],
        desired_replicas=int(specification.get("replicas", 1)),
        available_replicas=int(status.get("availableReplicas", 0)),
        generation=int(metadata["generation"]),
        observed_generation=int(status.get("observedGeneration", 0)),
        resource_version=str(metadata["resourceVersion"]),
    )


@dataclass(frozen=True)
class KubectlTransport:
    context: str
    runner: CommandRunner = _subprocess_runner
    binary: str = "kubectl"

    def run(self, *arguments: str) -> str:
        return self.runner((self.binary, "--context", self.context, *arguments))


@dataclass(frozen=True)
class KubernetesObserver:
    """Read-only environment observer, configured with separate credentials."""

    transport: KubectlTransport

    def deployment(self, namespace: str, name: str) -> DeploymentState:
        payload = self.transport.run(
            "--namespace",
            namespace,
            "get",
            "deployment",
            name,
            "--output=json",
        )
        return parse_deployment(payload)


@dataclass(frozen=True)
class KubernetesActuator:
    """Mutation-only adapter; it does not grade its own effects."""

    transport: KubectlTransport

    def set_replicas(self, namespace: str, name: str, replicas: int) -> None:
        if replicas < 0:
            raise ValueError("replicas must be non-negative")
        self.transport.run(
            "--namespace",
            namespace,
            "scale",
            f"deployment/{name}",
            f"--replicas={replicas}",
        )


@dataclass(frozen=True)
class ResetContract:
    namespace: str
    desired_replicas: Mapping[str, int]

    @classmethod
    def capture(
        cls, observer: KubernetesObserver, target: KubernetesTarget
    ) -> ResetContract:
        names = (target.incident_deployment, target.alternate_deployment)
        states = {
            name: observer.deployment(target.namespace, name) for name in names
        }
        if not all(state.converged for state in states.values()):
            raise RuntimeError("cannot capture reset contract from unconverged state")
        return cls(
            namespace=target.namespace,
            desired_replicas={
                name: state.desired_replicas for name, state in states.items()
            },
        )

    def restore(self, actuator: KubernetesActuator) -> None:
        for name, replicas in sorted(self.desired_replicas.items()):
            actuator.set_replicas(self.namespace, name, replicas)

    def verify(self, observer: KubernetesObserver) -> bool:
        return all(
            (state := observer.deployment(self.namespace, name)).converged
            and state.desired_replicas == replicas
            for name, replicas in self.desired_replicas.items()
        )
