# Iteration 19: domain-stratified complete-tuple substitution matrix

Timestamp: 2026-09-29T01:25:34Z

## Research question

Can complete trusted tuple binding plus execution-time evidence sealing preserve
benign utility while containing proposal-time and post-decision substitutions
of identity, tenant, resource, destination, provenance, and delegation?

## Competing explanations

- H1: schema validation is sufficient for these substitutions.
- H2: proposal-time binding is sufficient; rechecking the evaluated tuple at
  dispatch adds no coverage.
- H3: always-deny provides the same useful security outcome.
- H4: complete binding plus a broker-side seal preserves the paired benign
  actions while containing both substitution stages.
- H5: apparent containment comes from trusting the decision or receipt rather
  than independently observing the executed tuple.

## Smallest discriminating action

Freeze a two-repetition matrix over six authority dimensions, three synthetic
domains and protocols (retail/REST, calendar/GraphQL, document/SOAP), three
conditions (benign, proposal substitution, post-decision substitution), and
four controls (no defense, schema-only, SENTINEL, always-deny). Exercise the
actual Guardian trusted binder. Add a minimal execution verifier that compares
the exact canonical action presented to the broker with the evidence digest
authorized by policy. Grade the executed tuple independently of both decision
and receipt.

## Acceptance and falsification criteria

- 144 trials and 144 exact native-namespace round trips.
- Two fresh executions must be byte-identical.
- All 12 SENTINEL benign controls must execute as authorized; all 24 SENTINEL
  attacks must be contained.
- No-defense and schema-only must retain 12 benign controls each but contain
  zero attacks; always-deny must contain 24 attacks but retain zero benign
  controls.
- Across all conditions, 84 effects must include 36 authorized and 48
  unauthorized effects. Of 96 attack trials, 48 must be contained.
- Proposal-time SENTINEL reasons must be eight agent-asserted authority and four
  authorized-argument mismatches. All 12 post-decision substitutions must fail
  through evidence-digest mismatch.
- Receipt/effect comparisons must yield 36 agreements, 48 disagreements, and
  60 not-computable results.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/tuple_substitution_matrix.json`, SHA-256
  `476ba9287468324203cb3e467bb95eadd207a6a8c6bb5a38555d34acb1433f12`.
- Execution seal: `guardian/control_plane/execution.py`, SHA-256
  `9c8633ec3cf285ee548035b26efc207cbc7e892983750ba8c8c394e7ba38931b`.
- Control-plane export: `guardian/control_plane/__init__.py`, SHA-256
  `7a0c14a4faa18f1ba41eb4a6107f2701600135aa66a228e5ee661132f0da42ff`.
- Matrix implementation:
  `sentinel_experiments/tuple_substitution_matrix.py`, SHA-256
  `1521fdb78db84db5298207035105aebe2ce5b23bcf162c41b0c67ddfe2b3df1b`.
- Write-once runner: `scripts/run_tuple_substitution_matrix.py`, SHA-256
  `dd1e0c93a60e567b57324a2cfda8e5eadabcad2d6a7f6264e32b4f3abbabe4ad`.
- Focused tests: `tests/test_tuple_substitution_matrix.py`, SHA-256
  `c7dd03dad0807977b36c9b440b81054ba4ceb256714d981e96e63f153733b605`.
- Accepted raw report:
  `_workloads/reproduction/iteration-19-tuple-substitution-v1/report.json`,
  SHA-256
  `e8f632109b5befff5c0348f6b006bef8203b9f5d5bceb71f1a4b5d1f0b9b6737`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network,
  service, account, or external effect was invoked.

## Results

All preregistered counts passed, and a fresh rerun was byte-identical.

| Guardrail | Benign utility | Attacks contained |
|---|---:|---:|
| No defense | 12/12 | 0/24 |
| Schema-only | 12/12 | 0/24 |
| SENTINEL | 12/12 | 24/24 |
| Always-deny | 0/12 | 24/24 |

Across 144 trials, the independent exact-tuple oracle observed 84 effects: 36
matched the authorized tuple and 48 did not. There were 96 attack trials, split
evenly between 48 contained attacks and 48 unauthorized effects in the two
permissive controls.

SENTINEL's proposal boundary rejected identity, tenant, provenance, and
delegation authority injected into the agent proposal in eight trials. It
rejected four resource or destination argument changes against the complete
trusted argument tuple. The new execution seal rejected all 12 mutations made
after a successful policy decision. All 12 benign SENTINEL actions matched the
authorized digest and executed.

The focused matrix and binder suite passed 29 tests. The complete repository
test suite passed with two existing skips. The accepted report and independent
fresh report were byte-identical.

## Deviations

None from the frozen protocol. Formatting-only changes after the accepted run
did not alter experimental logic or the byte-identical report; final source
hashes above reflect the reviewed files.

## Limitations

This is a synthetic deterministic mechanism-coverage experiment. The domains
and REST, GraphQL, and SOAP labels exercise protocol evidence and different
tuple shapes, but they do not run real servers or serialized wire protocols.
The schema-only and no-defense controls are local controls, not reproductions of
published systems. There is no LLM, adaptive attack generation, concurrency,
TOCTOU race, key compromise, replay, or multi-step workflow.

The execution seal is a SHA-256 equality check whose expected digest is assumed
to arrive over a trusted control path. It is not signed, timestamped, scoped to
a nonce, or protected from replay. The independent oracle runs in the same
process and compares deterministic tuples; authenticated external telemetry is
still missing.

The result is partly construction-validating: a mechanism designed to bind and
seal the complete tuple should reject tuple changes. It establishes coverage
and preserves paired utility in these cases, not superiority, prevalence, or
an end-to-end security rate. Two repetitions establish reproducibility only,
not inferential sample size.

## Interpretation

H1, H2, H3, and H5 are rejected for the frozen matrix; H4 is supported. Schema
validation cannot establish who authorized a well-typed value. Proposal-time
binding alone leaves a time-of-check/time-of-use gap. Always-deny supplies
containment without useful execution. Combining trusted tuple construction
with an execution-time digest closes both tested substitution stages while
retaining the benign controls.

The narrow surviving mechanism claim is now: **bind every authority-bearing
attribute from trusted evidence, authorize the complete canonical tuple, and
require the execution broker to prove it is executing that same tuple**. The
effect oracle remains necessary because a valid receipt can accompany an
unauthorized effect in the permissive controls.

## Publication impact

This is the first domain-stratified positive SENTINEL result spanning identity,
tenant, resource, destination, provenance, and delegation at both proposal and
post-decision stages. It turns trusted complete-tuple binding from a one-policy
result into a six-dimension mechanism result and adds the previously absent
policy-to-execution seal.

It is not yet publication-grade efficacy evidence. Milestone 20 must compare
the surviving claim against CaMeL, Agent-C, Fides, and ToolGate evidence,
identify which dimensions are genuinely complementary, and decide whether the
paper is best framed as an assurance/evaluation architecture or a narrower
negative-results study. Later confirmatory work must use non-synthetic tasks,
published baselines, adaptive attacks, and authenticated observation.

The testing-strategy skill materially shaped the paired benign controls,
security-boundary unit test, full integration matrix, exact data-integrity
oracle, coverage targets, and the explicit list of untested deployment gaps.

## Decision

**Continue to milestone review.** Iteration 20 should audit whether trusted
complete-tuple construction plus a policy-to-execution seal and independent
effect correspondence remains a defensible contribution after subtracting
published baseline coverage. It must not promote these synthetic counts to an
efficacy claim.
