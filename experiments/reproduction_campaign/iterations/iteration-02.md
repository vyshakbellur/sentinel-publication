# Iteration 02: isolated environment and license audit

Timestamp: 2026-09-28T20:14:24Z

## Research question

Can the pinned AgentDojo and CaMeL artifacts be installed and pass their
model-free unit suites on the available host, and are their licenses and
dependency specifications adequate for a scientifically reproducible baseline?

## Competing explanations

- H1: the pinned artifacts install deterministically and their released tests
  pass without undocumented environment changes.
- H2: the artifacts are executable, but floating dependency specifications or
  host constraints prevent the installation itself from being called an exact
  reproduction.
- H3: at least one artifact cannot be exercised on the available host.

## Smallest discriminating action

Create separate Python 3.12 virtual environments at the exact pinned commits,
perform editable installs, and run only the released model-free unit suites.
Compare installed key packages with each repository's `uv.lock`, inspect the
licenses, and statically check Agent-C's archived environment for host-specific
requirements. No model API was invoked.

## Acceptance and falsification criteria

- Accept basic executability when installation succeeds and all collected unit
  tests pass at the pinned source revision.
- Accept deterministic environment recovery only when the released lock is
  applied or installed versions match it.
- Falsify an immediately portable Agent-C full-environment claim if its pinned
  requirements contain unconditional packages unavailable on Darwin arm64.
- H1 is falsified by any undocumented dependency step or lock drift; H3 is
  falsified for a baseline whose complete model-free unit suite passes.

## Exact artifacts and configuration

- Host: Darwin arm64, 16 GiB RAM.
- Interpreter: CPython 3.12.7 from `/opt/anaconda3/bin/python3.12`.
- AgentDojo commit: `089ed468cf3ed0322acc66b0211f26d9d90dbf60`.
- AgentDojo lock SHA-256:
  `395e3d0a59214515008d27c4462c9723ab7594374243f561ad5f19b3aa8a5330`.
- CaMeL commit: `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8`.
- CaMeL lock SHA-256:
  `0faab6087bf208c9829db502618af59ff2b911d2bacee9b7e61d221d371daf7c`.
- Agent-C Zenodo `requirements.txt` SHA-256:
  `9b6d8c392f1994cc6006d554df07d99ac1a6bd6081083788ed7fff4b957c5378`.
- Raw AgentDojo run:
  `_workloads/reproduction/iteration-02-agentdojo-env/`.
- Raw CaMeL run:
  `_workloads/reproduction/iteration-02-camel-env-v2/`.
- Interrupted first AgentDojo checkout, retained but not counted:
  `/tmp/sentinel-interrupted-runs/iteration-02-agentdojo-env-first-attempt/`.

The editable installations used `pip`, which resolves declared lower bounds to
current compatible packages; they did not apply `uv.lock`. CaMeL's development
dependencies are a PEP 735 dependency group rather than an install extra, so
`pip install -e '.[dev]'` did not install pytest. The released lock's
`pytest==8.3.5` was added explicitly before running the suite.

## Results

- AgentDojo installed and all 32 collected model-free tests passed.
- CaMeL installed and all 126 collected released tests passed after the
  documented pytest-runner correction.
- CaMeL's loose installation drifted substantially from its lock. Examples:
  AgentDojo 0.1.35 installed versus 0.1.34 locked; Anthropic 1.9.0 versus
  0.52.2; Google GenAI 2.25.0 versus 1.18.0; OpenAI 3.20.0 versus 1.82.1; and
  Pydantic AI 2.51.0 versus 0.2.12. The passing unit suite therefore establishes
  current-source compatibility, not recovery of the authors' environment.
- AgentDojo is MIT licensed, CaMeL is Apache-2.0, Fides is MIT, and the Agent-C
  Zenodo artifact is MIT. These licenses permit research integration subject
  to their notice requirements; third-party code remains external and pinned.
- Agent-C's archived full requirements unconditionally pin CUDA/NVIDIA packages,
  `torch==2.8.0`, and `triton==3.4.0`. That exact frozen environment is not
  directly portable to the Darwin arm64 host. Its lean `pyproject.toml` is
  separable and may support a later CPU-side tau2 artifact replication, but
  that would be a documented infrastructure substitution.

## Deviations

- Neither released `uv.lock` was applied because `uv` was not preinstalled.
  Installing the application under lower-bound specifications intentionally
  answered executability, not exact environment recovery.
- CaMeL's first test command failed because pytest was absent; no test executed.
  The same write-once run directory preserves that log, and the correction
  installed the exact pytest version declared by the released lock.
- No LLM-backed benchmark condition, native paper metric, or reported result was
  reproduced in this iteration.

## Limitations

Passing unit tests does not establish benchmark validity, defense efficacy, or
equivalence to the authors' model/API behavior. Current package releases may
also conceal incompatibilities not covered by the suites. The Agent-C finding
is a platform audit, not an attempt to install its CPU-compatible core.

## Interpretation

H1 is rejected. H2 is supported for AgentDojo and CaMeL: both are executable,
but a loose contemporary install cannot be labeled exact. H3 is rejected for
their model-free suites. The Agent-C full environment requires a Linux/CUDA
host or a separately labeled substitution path.

## Publication impact

The baseline methodology must report both source revision and environment
fidelity. A passing test suite under floating dependencies is insufficient for
a reproduction claim. The observed version drift is itself a useful artifact-
reproducibility warning, but not yet a research contribution. SENTINEL remains
uncompared until native AgentDojo tasks, attacks, and scorers are validated.

## Decision

**Continue.** In iteration 3, validate AgentDojo's native task/attack/scorer
wiring on the smallest no-cost smoke subset, keeping any local or mock model
result separate from paper-result reproduction.
