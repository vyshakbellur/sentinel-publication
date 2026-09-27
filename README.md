# SENTINEL

SENTINEL is an effect-grounded conformance and fault-injection harness for
evaluating deterministic boundaries around probabilistic agent workflows. The
target boundary treats every model input and output as data, binds actions to
trusted contracts and authority, validates dependency/conflict semantics,
mediates execution, and checks responses against independent effects. This
repository is intentionally separate from Guardian and ARIA:

- **ARIA** supplies fallible remediation proposals;
- **Guardian** is the bundled reference deterministic boundary under test;
- **SENTINEL** injects faults and grades conformance, actual effects, and
  recovery.

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

## Reproduce the non-live artifact checks

The clean-environment verifier creates a temporary virtual environment, applies
the complete runtime/test constraints in `requirements/repro.lock`, downloads and
checksum-verifies the locked OPA binary, and runs tests, lint, and reference
integrity checks:

```bash
python3.12 scripts/reproduce_artifact.py \
  --report artifacts/reproduction/local.json
```

The generated report records exact lock digests, a source-tree digest, command
outcomes, environment details, and limitations. Dependency and tool bootstrap
requires network access unless those artifacts are cached. This verifies the
non-live research artifact only; it neither provisions Kubernetes nor produces
live-system evidence.

## Fetch the locked public workloads

```bash
python scripts/fetch_workloads.py
```

This checks out exact commits beneath `_workloads/`; it does not vendor those
repositories or their histories into SENTINEL.

The external-policy baseline also uses a checksum-pinned OPA executable:

```bash
python scripts/fetch_tools.py
SENTINEL_OPA_BIN="$PWD/_tools/opa" python -m pytest
```

## Current experiment boundary

This slice uses a deterministic simulator, not a live Kubernetes cluster. Its purpose is to validate experiment contracts, oracle behavior, deterministic replay, and fault plumbing before expensive model or cluster runs. It does not establish production safety.

The publication target and evidence gates are specified in
`paper/DSN_2027_PLAN.md`. The primary-source gap review is in
`docs/DETERMINISTIC_BOUNDARY_LITERATURE_REVIEW.md`; the proposed multi-step,
multi-protocol design is in `docs/WORKFLOW_BOUNDARY_ARCHITECTURE.md`; and the
hostile-calendar benchmark is specified in
`docs/CASE_STUDY_CALENDAR_PROMPTWARE.md`. Those designs are planned work and
must not be described as implemented.
