# Live Kubernetes experiment boundary

## Requirements

SENTINEL must actuate a bounded remediation, observe the resulting environment
through independent credentials, and restore the exact pre-trial state before
the next randomized condition. A tool response is never accepted as evidence
that the effect occurred or that recovery succeeded.

Non-functional requirements are deterministic command construction, immutable
target revisions, unique trial identity, fail-closed parsing, and no production
cluster support. The initial action vocabulary is limited to Deployment replica
changes in disposable namespaces.

## Components and data flow

```text
frozen proposal -> guardrail -> KubernetesActuator -> Kubernetes API
                                          |              |
                                          |              v
terminal record <- effect oracle <- KubernetesObserver <- state
                         ^
                         |
                 independent context

pre-state -> ResetContract -> actuator restore -> observer verification
```

- `KubernetesActuator` has mutation credentials and never grades its own result.
- `KubernetesObserver` has a separate context intended for read-only RBAC.
- `ResetContract` captures only converged pre-state, restores deterministically,
  and requires independent convergence verification.
- `KubernetesTarget` maps neutral experiment roles to revision-pinned workload
  names and namespaces.

## Authorization and readiness gate

`deploy/kubernetes/experiment-rbac.json` creates distinct observer and actuator
service accounts in each disposable namespace. Observer authority is limited to
`get` on the two mapped Deployments. Actuator authority is limited to
`get`, `patch`, and `update` on the corresponding `deployments/scale`
subresources. Both Roles use `resourceNames`; neither can read Secrets.

Before a trial, `python -m scripts.check_kubernetes_readiness` verifies distinct
contexts, positive permissions required by each adapter, negative permissions
that enforce separation, and independently observed target convergence. Its
content-digested JSON result is an experiment input. A failed or malformed
check blocks execution.

`sentinel-live-pilot` binds one condition from the frozen protocol to the
uniform guardrail interface, reruns readiness, executes the fail-safe trial,
and creates one content-digested terminal record. It uses exclusive file
creation so a trial ID cannot silently overwrite earlier evidence. Failures in
decision evaluation or pre-state capture also produce a terminal record; a
failed readiness check produces no mutation.

The controller also binds every record to the frozen study partition, pairwise
design digest, phase-specific run-ID prefix, design row, and independent
deployment/incident/load block. Pilot and census records are marked
non-confirmatory. Primary-analysis validation recomputes record digests and
rejects non-confirmatory phases or mismatched protocol, design, and partition
digests. Confirmatory execution is locked until the blinded pilot yields a
versioned integer repetition count. Non-nominal rows are currently rejected
because live fault injection has not yet been implemented; this prevents a
nominal action from being mislabeled as a fault trial.

## Initial mappings

| System | Namespace | Incident target | Alternate target | Deployment source |
|---|---|---|---|---|
| Online Boutique | `sentinel-online-boutique` | `adservice` | `cartservice` | Pinned application Kubernetes manifests |
| OTel Astronomy Shop | `sentinel-otel-demo` | `ad` | `cart` | Pinned official OTel Demo Helm chart |

The application and Helm chart are separately pinned because the OTel Demo
application repository provides Compose definitions while its official
Kubernetes deployment is maintained in the OpenTelemetry Helm chart repository.

## Failure behavior

- Missing fields or malformed Kubernetes JSON fail the trial.
- An unconverged environment cannot become a reset baseline.
- Negative replica requests are rejected before invoking Kubernetes.
- Failed restoration, actuator timeout, stale observation, partial effect, and
  rollback failure remain terminal outcomes; they are not silently excluded.
- A trial may begin only after the reset contract verifies through the observer.

## Trade-offs

Replica scaling provides a portable, observable first action but does not cover
configuration patches, rollouts, network policy, or persistent data. CLI-based
adapters are slower than a Kubernetes client library, but make exact commands
auditable and avoid adding a large client dependency. Separate kube contexts
improve independence but still share the Kubernetes API server; later work
should add audit-log receipts. Dedicated service accounts and resource-scoped
RBAC are included in the current pilot boundary.

## Revisit after the pilot

Calibrate convergence and recovery windows, add rollout and partial-commit
actions, validate RBAC behavior on a disposable API server, and decide whether
API-server audit events or a side-channel controller should become the
authoritative effect log.
