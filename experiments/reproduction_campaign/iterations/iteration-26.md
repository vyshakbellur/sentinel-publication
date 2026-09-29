# Iteration 26: cross-layer boundary faults and minimal assurance cut sets

Timestamp: 2026-09-29T03:08:40Z

## Research question

Under the four boundary-fault primitives frozen at milestone 24, what are the
minimal SENTINEL fault sets that cause (a) any unauthorized effect and (b) an
unauthorized effect omitted by the system observer?

## Competing explanations

- H1: a single adapter, broker, or observer fault silently defeats the entire
  SENTINEL assurance chain.
- H2: adapter and broker faults independently defeat prevention, while a
  healthy effect observer still exposes the unauthorized effect.
- H3: an observer fault alone creates an unauthorized effect.
- H4: silent compromise requires observer omission plus a prevention-layer
  fault, producing a two-fault minimal cut set in the constructed SENTINEL
  chain.
- H5: detected unauthorized effects can be counted as successful containment.

## Smallest discriminating action

Hold the ten development attack actions and five benign actions fixed. Execute
them once across no-defense, always-deny, correct-label Fides reconstruction,
the frozen mislabeled-Fides adapter fault, nominal SENTINEL, and every subset
of the three frozen SENTINEL adapter, broker, and observer fault primitives.
Keep the system observer separate from the independent research oracle, then
minimize prevention and silent-compromise cut sets by subset inclusion.

## Acceptance and falsification criteria

- Execute 180 trials with exact native-namespace round trips and a
  byte-identical fresh rerun.
- Preserve 5/5 benign actions in every condition except always-deny.
- Record all unauthorized effects as failures even when the system observer
  detects them.
- A single SENTINEL adapter or broker fault must create ten independently
  observed unauthorized effects; an observer-only fault must create none.
- Minimal prevention cut sets must be `{adapter}` and `{broker}`.
- Minimal silent cut sets must be `{adapter, observer}` and `{broker,
  observer}`; any singleton silent cut set falsifies H4.
- Do not inject any fault outside the four frozen primitives or inspect a
  confirmatory holdout.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/boundary_fault_cutsets.json`, SHA-256
  `428ff4d07cc6e88bdce662c2e870120ceac383074207f234dfd8349b2ad53a32`.
- Fault harness, trace builder, independent oracle, and cut-set minimizer:
  `sentinel_experiments/boundary_faults.py`, SHA-256
  `42b05891c074c4df4fa098f9d3b7d85da868539a9cf36b70541b1c4dd8182968`.
- Write-once runner: `scripts/run_boundary_fault_cutsets.py`, SHA-256
  `3b7847ae5b040d5f39851fa36379fae52f27fb440f9ddef8ba6dbd8d7823b7b4`.
- Focused tests: `tests/test_boundary_faults.py`, SHA-256
  `7242531378c7b25c4e5bd77c3448ae48dd35259ca8977966a5c377b2c193d4d0`.
- Accepted raw report:
  `_workloads/reproduction/iteration-26-boundary-fault-cutsets-v1/report.json`,
  SHA-256
  `dbb54433f3d38e1b3f7f23cf59c6332ca374b1215eada8eddd15b8c3a8a061d0`.
- Hash-bound inputs: milestone 24 `3dcea978...` and iteration 25
  `f907098b...`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network, real
  service, file payload, credential, or external effect was invoked.

## Results

All preregistered counts passed. The accepted and fresh reports were
byte-identical. Ten focused tests and the full repository suite passed with two
existing skips.

| Condition | Benign utility | Safe attack utility | Unauthorized effects | Detected by SENTINEL observer | Silent effects |
|---|---:|---:|---:|---:|---:|
| No defense | 5/5 | 0/10 | 10 | N/A | N/A |
| Always deny | 0/5 | 0/10 | 0 | N/A | N/A |
| Fides correct-label reconstruction | 5/5 | 10/10 | 0 | N/A | N/A |
| Fides mislabeled adapter | 5/5 | 0/10 | 10 | N/A | N/A |
| SENTINEL nominal | 5/5 | 10/10 | 0 | 0 | 0 |
| SENTINEL adapter fault | 5/5 | 0/10 | 10 | 10 | 0 |
| SENTINEL broker fault | 5/5 | 0/10 | 10 | 10 | 0 |
| SENTINEL observer fault | 5/5 | 10/10 | 0 | 0 | 0 |
| SENTINEL adapter + broker | 5/5 | 0/10 | 10 | 10 | 0 |
| SENTINEL adapter + observer | 5/5 | 0/10 | 10 | 0 | 10 |
| SENTINEL broker + observer | 5/5 | 0/10 | 10 | 0 | 10 |
| SENTINEL adapter + broker + observer | 5/5 | 0/10 | 10 | 0 | 10 |

Across 180 trials, 80 unauthorized effects occurred. Thirty SENTINEL effects
were detected by the system observer and 30 were silent under an observer
fault. Receipt versus safe-effect comparison yielded 85 agreements, 80
disagreements, and 15 not-computable outcomes. System-observer versus
independent-effect comparison yielded 90 agreements, 30 disagreements, and 60
not-computable non-SENTINEL outcomes.

The minimal SENTINEL prevention cut sets were the singletons:

- `{sentinel_adapter_fault}`
- `{sentinel_broker_fault}`

The minimal SENTINEL silent-compromise cut sets were:

- `{sentinel_adapter_fault, sentinel_observer_fault}`
- `{sentinel_broker_fault, sentinel_observer_fault}`

Supersets were correctly excluded by subset minimization. Detection never
earned prevention credit: all 30 detected unauthorized effects remained
security failures.

## Deviations

None from the frozen experimental protocol. An optional Ruff check could not
run because Ruff is not installed; the focused and complete Python test suites
were rerun after the final formatting change. This did not change an
experimental condition or evidence report.

## Limitations

Fault behavior is a deterministic in-memory model, not observed component
reliability or a production chaos experiment. The cut-set sizes are structural
properties of this constructed chain, not probabilities, failure rates, or
claims of Byzantine fault tolerance. Correlated faults and shared dependencies
are not modeled.

The independent research oracle remains in process and is trusted by the
analysis. SENTINEL's system observer detects rather than reverses effects, so
the result establishes detection redundancy, not single-fault prevention.
The Fides condition is a conceptual reconstruction and has no comparable
native effect-observer layer; its adapter-fault result cannot support a fair
cross-family cut-set-size superiority claim.

No official baseline, real multi-service action, independently authenticated
observer, stochastic component, confidence interval, or confirmatory holdout
was added.

## Interpretation

H1, H3, and H5 are rejected; H2 and H4 are supported in the constructed
model. SENTINEL is not one-fault-safe for prevention: either a trusted adapter
or broker failure can cause an unauthorized effect. Its distinct assurance
property is narrower and defensible—a separate observer changes a silent
failure into a detected failure unless the observer also fails.

This sharpens the paper contribution from “deterministic guardrails stop
prompt injection” to “effect-grounded fault analysis reveals which trusted
layers must fail for prevention and detection guarantees to diverge.” The
negative result is equally important: nominal enforcement and content attacks
alone cannot establish this property.

## Publication impact

Minimal cross-layer assurance cut sets move from untested to
development-supported as the strongest surviving research direction. The
experiment supplies a concrete taxonomy, trace semantics, minimization method,
and falsifiable distinction between effect prevention and silent compromise.
It still does not make the paper publication-ready because external validity,
real effects, authenticated observation, and confirmatory evidence remain
missing.

The testing-strategy skill shaped the separate prevention/detection outcomes,
always-deny utility control, singleton falsification tests, source-namespace
separation, and data-integrity checks.

## Decision

**Continue to iteration 27.** Freeze this cut-set interpretation, then execute
the five predeclared confirmatory holdout identifiers without tuning. Report
each case individually, preserve missing evidence, and do not use deterministic
case count as a population confidence interval. If holdout construction cannot
be made independent of the development mechanism, explicitly downgrade it
rather than labeling it confirmation.
