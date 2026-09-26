# Disposable Kubernetes pilot checklist

This checklist is an execution gate, not evidence that a live pilot occurred.
Use only a disposable, non-production cluster dedicated to SENTINEL trials.

## Before deployment

- Confirm the active administrator context names the disposable cluster.
- Confirm the workload revisions match `external/workloads.lock.json`.
- Run the complete test and lint suites from a clean checkout.
- Apply `deploy/kubernetes/experiment-rbac.json` as an administrator.
- Deploy each pinned workload into its mapped namespace without renaming the
  four target Deployments.
- Create separate kube contexts backed by the `sentinel-observer` and
  `sentinel-actuator` service accounts; never reuse the administrator context.
- Run `python -m scripts.check_kubernetes_readiness` and retain its JSON report.
- Require `ready: true`, a verified report digest, and a converged baseline
  before scheduling any trial.

## Pilot execution

- Replace the contract-only identifiers in
  `experiments/protocol/pilot_blocks_contract.json` with three real independent
  deployment/load blocks per system in an execution-local file. Generate and
  audit the immutable order before the first trial:

  ```sh
  PYTHONPATH=. python scripts/generate_pilot_schedule.py \
    --blocks /path/to/live-pilot-blocks.json \
    --output /path/to/live-pilot-schedule.json \
    --audit-output /path/to/live-pilot-schedule-audit.json
  ```

  Require 360 unique cells, 60 rows per system block, three repetitions of each
  system/guardrail/design-row cell, valid study bindings, and matching schedule,
  protocol, design, and partition digests. Never execute the checked-in contract
  schedule; its deployment identifiers are placeholders.
- Begin with one nominal row and one blocked row per system.
- Execute each row through the single-row controller, for example:

  ```sh
  python -m sentinel_experiments.pilot_cli \
    --trial-id PILOT-online-none-001 \
    --system online-boutique \
    --guardrail none \
    --phase pilot \
    --design-row-id PW000 \
    --deployment-instance-id online-deploy-001 \
    --incident-template-id replicas-zero-v1 \
    --load-seed seed-001 \
    --observer-context sentinel-observer \
    --actuator-context sentinel-actuator \
    --output experiments/runs/PILOT-online-none-001.json
  ```

  The output path must not exist. The controller rejects conditions absent from
  the frozen protocol, enforces the phase-specific row allocation and trial-ID
  prefix, binds the independent deployment/incident/load block, reruns readiness
  immediately before mutation, stores protocol/design/partition/readiness
  digests, and refuses to overwrite a prior record. Controller-level adapters
  implement all 11 single-fault rows. Enforcement rows emit per-attempt broker
  receipts for requested/executed target, submission, completion, bypass, drop,
  and retry identity. These receipts are controller contract evidence until
  calibrated against Kubernetes API audit events on the disposable cluster.
- Preserve randomized trial identity, proposal, observations, state-machine
  phases, oracle output, errors, and restoration result in the terminal record.
- Do not retry or exclude a failed trial based on its outcome. Record the
  failure and apply the frozen exclusion rules during analysis.
- Verify the reset contract before advancing to the next row.
- Execute the frozen schedule order without outcome-based reordering. Stop the
  batch after any unsuccessful terminal record, especially a restoration
  failure; resume only through a recorded protocol decision.
- Give the pilot analyst a keyed blinded projection that omits guardrail labels
  and randomization keys. Keep the operational label mapping separate until
  sample size and analysis choices are frozen.

## Rollback triggers

Stop the pilot immediately if any of these occurs:

- the readiness report fails or either context resolves to the wrong cluster;
- the observer can mutate a Deployment or the actuator can read a Secret;
- a mapped Deployment is absent, renamed, or fails to converge;
- a record/spec/report digest does not match;
- restoration cannot reproduce and independently verify the captured state;
- an unexpected namespace, resource, or action is observed.

On a stop, preserve records and cluster events, restore through the bounded
actuator if safe, verify through the observer, and destroy the disposable
cluster if restoration is uncertain. Never broaden RBAC to make a failed check
pass without recording and reviewing the protocol deviation.

## After the pilot

- Re-run record and manifest integrity checks before analysis.
- Inspect all restoration failures and observation disagreements.
- Calibrate recovery windows without looking at guardrail identities.
- Freeze repetition count and analysis changes before confirmatory execution.
- Replace the pending repetition marker in the frozen partition only through a
  versioned post-pilot amendment; confirmatory execution remains software-locked
  until this occurs.
- Record exact cluster, Kubernetes, client, workload, and tool versions.
