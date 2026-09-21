# SENTINEL

SENTINEL is an effect-grounded fault-injection harness for evaluating deterministic guardrails around predictive action systems. This repository is intentionally separate from Guardian and ARIA:

- **ARIA** supplies fallible remediation proposals;
- **Guardian** is the bundled reference deterministic guardrail under test;
- **SENTINEL** injects faults and grades actual effects and recovery.

This private research monorepo contains a provenance-recorded snapshot of the
Guardian reference implementation. The public `guardian-workshop` remains an
educational artifact; ARIA remains an independent predictor repository and is
connected through frozen proposal records. See
`docs/adr/0001-private-research-monorepo.md` for the boundary decision.

The first vertical slice uses Guardian's real trusted-attribute binder and policy pipeline with a deterministic microservice simulator. It covers nominal recovery plus predictor, binding, policy, enforcement, and observation faults. Public systems used for live experiments are locked in `external/workloads.lock.json` and fetched into an ignored directory.

## Run the initial experiment

```bash
python -m pip install -e ".[dev]"
python -m sentinel_experiments.cli \
  --output experiments/runs/e0-guardian-smoke-v1
```

The command writes:

- `manifest.json`: frozen matrix and implementation metadata;
- `results.jsonl`: one immutable terminal record per trial;
- `summary.json`: effect-grounded aggregate metrics.
- `cut_sets.json`: minimized fault combinations preserving unsafe outcomes.

Output directories are write-once by default. Choose a new run ID rather than overwriting evidence.

## Test

```bash
python -m pytest
python -m ruff check sentinel_experiments tests scripts
```

## Fetch the locked public workloads

```bash
python scripts/fetch_workloads.py
```

This checks out exact commits beneath `_workloads/`; it does not vendor those
repositories or their histories into SENTINEL.

## Current experiment boundary

This slice uses a deterministic simulator, not a live Kubernetes cluster. Its purpose is to validate experiment contracts, oracle behavior, deterministic replay, and fault plumbing before expensive model or cluster runs. It does not establish production safety.

The publication target and evidence gates are specified in
`paper/DSN_2027_PLAN.md`.
