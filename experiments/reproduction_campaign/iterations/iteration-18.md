# Iteration 18: independent environment-effect oracle matrix

Timestamp: 2026-09-29T01:09:37Z

## Research question

Does an independently observed environment effect change conclusions drawn
from guardrail decisions and execution receipts across controlled boundary
failures, beyond the single ToolGate false-success fixture in iteration 17?

## Competing explanations

- H1: decisions and executor receipts are sufficient; effect observation never
  changes a trial conclusion.
- H2: final state is sufficient; a separate event log adds no information.
- H3: independent effects expose successful-looking wrong-target, false-success,
  duplicate, and partial executions that upstream records or final state hide.
- H4: any apparent benefit is only refusal; always-deny is as useful as the
  guarded nominal path.
- H5: the common trace silently changes native trial objects or imputes missing
  values.

## Smallest discriminating action

Freeze and execute a deterministic seven-condition matrix twice from identical
fresh states: guarded nominal, no-defense wrong target, always-deny nominal,
post-decision argument substitution, false success, duplicate retry, and
partial effect. Keep decisions and receipts in a native object. Grade actual
effects and final state with the existing independent oracle, then place both
in the iteration-17 action/effect trace without modifying the native object.

## Acceptance and falsification criteria

- Fourteen trials and fourteen exact native-namespace round trips.
- Two fresh executions must be byte-identical.
- The nominal guardrail must yield two safe recoveries; always-deny must be safe
  but yield no recovery; no-defense wrong target must be unauthorized.
- The independent oracle must identify eight unauthorized effects, ten claimed
  successes without safe recovery, and eight claimed/actual recovery
  disagreements.
- The 56 preregistered comparisons must yield 26 agreements, 18 disagreements,
  and 12 not-computable results, with all per-comparison counts matching the
  frozen protocol.
- Missing receipts or targets must remain not-computable rather than become
  false.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/effect_oracle_matrix.json`, SHA-256
  `8c2e15ccab7297980dca3189e9acb6e2d3b030a57bac3616c70edabdb0c6d8e1`.
- Extended common trace implementation:
  `sentinel_experiments/action_effect_trace.py`, SHA-256
  `a3f78323cecef79a0f3407f6dd161780a05b29a80b6653ef283de43861104c0f`.
- Matrix implementation: `sentinel_experiments/effect_oracle_matrix.py`,
  SHA-256
  `83566a7bbd12ac54a7437fc681db3796c4c3158ad1b7ee23e748c2cedab177f6`.
- Write-once runner: `scripts/run_effect_oracle_matrix.py`, SHA-256
  `ec3d4fe7fcd8c53cd511f05f336d8a9d2a833a5cc0ae2365c69c11e662c1b70e`.
- Focused matrix tests: `tests/test_effect_oracle_matrix.py`, SHA-256
  `e0b2cd34af8292d5c9edd2e91eeffab88b1d3c6c0c8009138e938d6fb244c533`.
- Common-trace tests: `tests/test_action_effect_trace.py`, SHA-256
  `61ab95dc38cff721489249c69569f5a9a44e6efeec320f7057f0e203acee0ec5`.
- Accepted raw report:
  `_workloads/reproduction/iteration-18-effect-oracle-matrix-v1/report.json`,
  SHA-256
  `2acd20cc25f43aa4baed3ecf9fc3436a4e9c3d640be3d60551ee1efda4966a20`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network,
  service, malware, or external environment was invoked.

## Results

All preregistered criteria passed. The two independent fresh executions were
byte-identical.

| Outcome | Count |
|---|---:|
| Trials / exact native round trips | 14 / 14 |
| Safe recovery | 2 |
| Unauthorized effect | 8 |
| Claimed success without safe recovery | 10 |
| Claimed/actual recovery disagreement | 8 |
| Comparison agree / disagree / not computable | 26 / 18 / 12 |

The independent layer changed the conclusion in five faulted conditions per
repetition. Wrong-target execution completed and received a positive receipt
but did not recover the authorized service. False success had a completed
receipt but no effect. Duplicate retry recovered the expected final state, yet
the event and receipt logs exposed a duplicate unsafe action. Partial execution
had a positive receipt but an incomplete effect. Argument substitution was
visible as an exact authorized-target/observed-target disagreement.

Always-deny produced no unauthorized effect but also no recovery. It therefore
remains a safety control, not a useful-defense success. The guarded nominal
condition was the only condition with both safety and recovery.

The focused 11 tests passed, including scalar-type and null-missingness
invariants. The full repository suite passed with two existing skips.

## Deviations

The first direct runner invocation omitted the repository root from Python's
module search path and failed before creating an output. Re-running with
`PYTHONPATH=.` produced the accepted write-once artifact. This was an execution
environment issue, not an experimental trial, and no result was overwritten.

The protocol requests byte-identical fresh runs; the second report was written
to a temporary directory and compared to the accepted artifact, rather than
stored as a second permanent raw report.

## Limitations

This is a deterministic synthetic fault-injection validation, not an estimate
of real-world fault prevalence or end-to-end defense efficacy. The two
repetitions establish deterministic replay, not statistical independence.
Faults are isolated and developer-selected; adaptive attackers and combined
cut sets remain untested.

The effect observer shares process memory with the fixture. It is logically
independent because the oracle receives no policy verdict and does not trust a
tool success flag, but it is not yet a separately authenticated telemetry
channel. The matrix has one operation, two services, one tenant, no delegation,
and no concurrency. Its positive result validates the evaluation method, not a
broad production claim.

## Interpretation

H1, H2, H4, and H5 are rejected for the frozen cases; H3 is supported. Receipt
completion, final-state recovery, and safe recovery are not interchangeable.
In particular, the duplicate condition proves that final state alone can hide
an unsafe execution, while false success proves that a receipt can claim an
effect that never occurred.

The most defensible emerging contribution is therefore an **effect-grounded
assurance evaluation layer** coupled to complete trusted action-tuple binding.
The result does not establish that SENTINEL prevents these faults; it
establishes that its proposed evidence model can distinguish them without
crediting denial as utility or converting missing evidence to false.

## Publication impact

This extends the cross-layer disagreement result from one selected ToolGate
record to five controlled failure classes with explicit controls. It supplies
a reproducible measurement primitive and a negative result for receipt-only or
final-state-only evaluation. A publishable efficacy claim still requires
domain-stratified substitution trials, independently authenticated observation,
multiple protocols/workflows, and a frozen confirmatory partition.

The testing-strategy skill materially shaped the paired controls, boundary and
data-integrity cases, separation of focused contract tests from end-to-end
matrix checks, and explicit coverage gaps.

## Decision

**Continue.** Iteration 19 should test identity, tenant, resource, destination,
provenance, and delegation substitutions on a domain-stratified action matrix.
It must distinguish proposal-time rejection from post-decision substitution,
preserve a benign utility control for every action, and use this independent
effect oracle rather than receipts alone.
