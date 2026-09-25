"""Fail-closed readiness checks for disposable Kubernetes experiments."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Callable
from dataclasses import asdict, dataclass

from .kubernetes import KubectlTransport, KubernetesObserver, KubernetesTarget


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ReadinessReport:
    schema_version: str
    observer_context: str
    actuator_context: str
    checks: tuple[ReadinessCheck, ...]

    @property
    def ready(self) -> bool:
        return bool(self.checks) and all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "observer_context": self.observer_context,
            "actuator_context": self.actuator_context,
            "ready": self.ready,
            "checks": [asdict(check) for check in self.checks],
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        payload["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
        return payload


def _can_i(
    transport: KubectlTransport,
    verb: str,
    resource: str,
    namespace: str,
    resource_name: str | None = None,
) -> bool:
    arguments = ["auth", "can-i", verb, resource, "--namespace", namespace]
    if resource_name is not None:
        arguments.extend(("--resource-name", resource_name))
    response = transport.run(*arguments).strip().lower()
    if response not in {"yes", "no"}:
        raise ValueError(f"unexpected kubectl auth response: {response!r}")
    return response == "yes"


def check_kubernetes_readiness(
    observer_transport: KubectlTransport,
    actuator_transport: KubectlTransport,
    targets: dict[str, KubernetesTarget],
) -> ReadinessReport:
    """Verify context separation, least privilege, and target convergence.

    The checker does not mutate the cluster. Any command, parse, authorization,
    or convergence failure becomes a failed check rather than being skipped.
    """

    checks: list[ReadinessCheck] = []
    contexts_distinct = (
        bool(observer_transport.context)
        and bool(actuator_transport.context)
        and observer_transport.context != actuator_transport.context
    )
    checks.append(
        ReadinessCheck(
            "contexts-distinct",
            contexts_distinct,
            "observer and actuator kube contexts are non-empty and distinct",
        )
    )
    if not contexts_distinct:
        return ReadinessReport(
            "sentinel.kubernetes-readiness.v1",
            observer_transport.context,
            actuator_transport.context,
            tuple(checks),
        )

    observer = KubernetesObserver(observer_transport)

    def record(name: str, expectation: str, operation: Callable[[], bool]) -> None:
        try:
            passed = operation()
            detail = expectation if passed else f"FAILED: {expectation}"
        except (
            KeyError,
            OSError,
            subprocess.SubprocessError,
            TypeError,
            ValueError,
        ) as error:
            passed = False
            detail = f"ERROR: {type(error).__name__}: {error}"
        checks.append(ReadinessCheck(name, passed, detail))

    for system, target in sorted(targets.items()):
        names = (target.incident_deployment, target.alternate_deployment)
        for name in names:
            record(
                f"{system}:{name}:observer-get",
                "observer can get the mapped deployment",
                lambda t=target, n=name: _can_i(
                    observer_transport,
                    "get",
                    "deployments.apps",
                    t.namespace,
                    n,
                ),
            )
            record(
                f"{system}:{name}:observer-no-patch",
                "observer cannot patch the deployment scale",
                lambda t=target, n=name: not _can_i(
                    observer_transport,
                    "patch",
                    "deployments.apps/scale",
                    t.namespace,
                    n,
                ),
            )
            record(
                f"{system}:{name}:actuator-patch",
                "actuator can patch the mapped deployment scale",
                lambda t=target, n=name: _can_i(
                    actuator_transport,
                    "patch",
                    "deployments.apps/scale",
                    t.namespace,
                    n,
                ),
            )
            record(
                f"{system}:{name}:available",
                "mapped deployment exists and is converged",
                lambda t=target, n=name: observer.deployment(
                    t.namespace, n
                ).converged,
            )
        record(
            f"{system}:actuator-no-secrets",
            "actuator cannot get secrets",
            lambda t=target: not _can_i(
                actuator_transport, "get", "secrets", t.namespace
            ),
        )

    return ReadinessReport(
        "sentinel.kubernetes-readiness.v1",
        observer_transport.context,
        actuator_transport.context,
        tuple(checks),
    )
