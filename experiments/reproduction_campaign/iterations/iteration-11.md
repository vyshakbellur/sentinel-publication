# Iteration 11: SENTINEL complete-tuple binding comparison

Timestamp: 2026-09-28T23:17:44Z

## Research question

Can a minimal SENTINEL trusted intent envelope preserve the valid Agent-C
address-change case while rejecting every resource or destination-field
substitution admitted by schema validation or the released temporal rule?

## Competing explanations

- H1: complete tuple comparison is equivalent to always-deny and destroys the
  valid operation.
- H2: schema/type validation is sufficient for the mutation matrix.
- H3: the SENTINEL binder blocks only the resource identifier, duplicating the
  released Agent-C result.
- H4: exact binding of the authenticated action tuple admits the baseline and
  rejects all seven one-field mutations.

## Smallest discriminating action

Extend the existing trusted capability manifest with an opt-in
`bind_all_arguments` obligation and the trusted binding context with an
`authorized_arguments` tuple. Compare four deterministic subjects on the exact
eight labels and values from iteration 10: released Agent-C results,
schema-only validation, always-deny, and SENTINEL. Keep both order IDs inside
the allowed resource scope so SENTINEL's order rejection is attributable to
tuple mismatch rather than a narrower allowlist.

## Acceptance and falsification criteria

- The Agent-C input report must have SHA-256
  `b5bfaf4230cde569ede6f00098830d8fe483fa676c2a00f127105eaa6387c57d`
  and exactly the same eight case labels.
- SENTINEL must admit the unmodified baseline.
- SENTINEL must deny the order mutation and each of the six address-field
  mutations with a fail-closed tuple-mismatch reason.
- Schema-only must admit all well-typed cases, demonstrating that type safety
  is not authorization.
- Always-deny must deny the baseline, demonstrating why mutation blocking
  alone is insufficient.
- The result is a mechanism comparison, not an estimate of exploit frequency.

## Exact artifacts and configuration

- Parent Agent-C report: iteration 10 accepted v2, SHA-256 above.
- SENTINEL model changes:
  - `guardian/control_plane/models.py`, SHA-256
    `feba66703a89949fd1e357ebba142771134ed10d3d093bd0787e1f0974c1233a`;
  - `guardian/control_plane/binder.py`, SHA-256
    `d1fc59a47874414ba0d32337f109a6671ebffb615baadc3175c00d94dae7c870`.
- Comparison runner:
  `scripts/compare_agent_c_sentinel_tuple_binding.py`, SHA-256
  `9a313e27ae390a896e84cd8c2225ae3991d177eda87fffcf87841eb4be945a39`.
- Accepted raw report:
  `_workloads/reproduction/iteration-11-sentinel-tuple-v2/report.json`,
  SHA-256
  `6e6437a4f02eea0c475e9062e4096633a5a1e601a3d2b38f5b3899f9eb1756c1`.
- Preserved first successful run:
  `_workloads/reproduction/iteration-11-sentinel-tuple-v1/report.json`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model or external service
  was used.

## Results

The paired deterministic matrix produced:

| Subject | Valid baseline | Mutations blocked |
|---|---:|---:|
| Schema-only | 1/1 | 0/7 |
| Released Agent-C rule | 1/1 | 1/7 |
| Always-deny | 0/1 | 7/7 |
| SENTINEL exact tuple binding | 1/1 | 7/7 |

SENTINEL returned `ALLOW` for the unchanged tuple. It returned
`ERROR_FAIL_CLOSED` with `AUTHORIZED_ARGUMENT_VALUE_MISMATCH` for the changed
order ID and independently for `address1`, `address2`, `city`, `state`,
`country`, and `zip`. Both order IDs were valid same-tenant catalog resources
and were in the policy's allowed scope.

The bound capability now fails closed when the trusted tuple is absent, when a
value differs, when an argument name differs, or when a required argument is
omitted. The accepted canonical action records a digest of the authorized
arguments in its trusted protocol evidence. The capability's tuple-binding
obligation is part of the manifest digest.

The full repository suite passed: 249 tests were collected, with two existing
skips. The optional Ruff command was unavailable on this host; Python bytecode
compilation, targeted binder tests, the full pytest suite, and `git diff
--check` passed.

## Deviations

Iteration 10 did not emit the mutation values into its JSON report, only their
case labels and outcomes. This runner uses the identical constants from the
pinned iteration-10 runner and fails if the accepted report's case-label set
differs. Future shared matrices should be frozen as a standalone protocol
artifact before both subjects run.

The first successful run preceded a defensive type check for malformed trusted
context. It is preserved as v1. The accepted v2 result ran after the final
binding code and produced the same decision vector.

## Limitations

The trusted action tuple is supplied directly. This iteration does not solve
how free-form user intent becomes an authenticated tuple, how a user approves
it, or how amendments are authorized. It performs no tool execution and does
not test whether the resulting external effect matches the approved tuple.

Eight deterministic cases from one retail operation cannot support a general
security or utility rate, a confidence interval, or a claim of superiority
over Agent-C as a whole. Agent-C is evaluated from its released formula via the
iteration-10 artifact replication, while SENTINEL is a local implementation;
this is not a matched end-to-end model comparison.

Exact equality can also be too strict for semantically equivalent normalized
inputs. The binder currently applies JSON and Unicode normalization, but
domain-level equivalence and deliberately authorized wildcards/ranges need an
explicit contract language rather than ad hoc relaxation.

## Interpretation

H1, H2, and H3 are rejected on this matrix; H4 is supported. The useful
difference is not determinism alone. It is a trusted manifest obligation that
requires every action argument to equal the authenticated tuple, combined with
fail-closed omission handling. This occupies a narrower position than temporal
conformance: Agent-C correctly bound the action and order identity, while
SENTINEL additionally bound the value-bearing destination fields.

The testing-strategy discipline materially affected the experiment: the
schema-only and always-deny controls separate authorization completeness from
mere structural validity and trivial security, and the omission unit test
covers a distinct failure mode outside the seven value mutations.

## Publication impact

This is the first positive SENTINEL mechanism result against a released real
policy, with a utility sanity control. It supports the phrase **complete
authenticated action-tuple binding** rather than the overbroad phrase
“deterministic guardrails.” The publishable claim still requires a systematic
policy inventory, multiple operation families, realistic trusted-envelope
construction, tool execution, and independent effect observation.

## Decision

**Continue.** Iteration 12 is the scheduled milestone review. It should audit
all released Agent-C mutation policies for which authority-bearing parameters
are explicit variables versus wildcards, replay a stratified set beyond address
changes, and decide whether complete-tuple binding remains a general empirical
gap or only a single-policy counterexample. Do not expand to model-backed runs
until that coverage question is resolved.
