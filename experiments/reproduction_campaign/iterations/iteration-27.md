# Iteration 27: confirmatory-validity audit and prospective challenge matrix

Timestamp: 2026-09-29T03:23:45Z

## Research question

Were the five milestone-24 identifiers sufficient to constitute a valid frozen
confirmatory partition, and—if not—does a transparently post-development
instantiation expose a failure absent from the development matrices?

## Competing explanations

- H1: freezing names alone is sufficient to label later-authored fixtures as
  held-out confirmation.
- H2: a valid confirmation requires executable inputs, initial states, scoring
  rules, and analysis semantics fixed before development outcomes are known.
- H3: SENTINEL generalizes without qualification to all five named compound
  cases.
- H4: a false failure receipt can cause a duplicate effect that SENTINEL
  detects but does not prevent, exposing a prevention gap.
- H5: five purposively constructed deterministic cases support a population
  confidence interval.

## Smallest discriminating action

Search the repository for every frozen identifier and audit what milestone 24
actually fixed. Because no executable fixtures, states, scorers, or outcomes
existed, explicitly downgrade confirmation. Instantiate the five names as a
post-development prospective synthetic challenge set, freeze their full
semantics before execution, and run them once across no defense, schema-only,
correct-label Fides reconstruction, SENTINEL, and always-deny. Include one
duplicate-effect case that fails unless the second effect is actually
prevented.

## Acceptance and falsification criteria

- Never label the post-development cases as held-out confirmation.
- Execute 25 deterministic trials with exact native-namespace round trips and
  a byte-identical fresh rerun.
- Always-deny receives no utility credit.
- Detection after an unauthorized effect receives no prevention credit.
- The duplicate-effect case remains a SENTINEL failure unless an idempotency
  mechanism prevents the second effect.
- Report each case descriptively and do not compute an uncertainty interval
  from five non-random, non-exchangeable cases.
- Any divergence from these rules falsifies the validity audit.

## Exact artifacts and configuration

- Protocol and post-development case definitions:
  `experiments/protocol/prospective_challenge_matrix.json`, SHA-256
  `5263cba1219b5c493b37283d852e44e0b91299c6058cb4c689378c6b84661b3e`.
- Challenge harness and independent oracle:
  `sentinel_experiments/prospective_challenges.py`, SHA-256
  `347b5f3aaa4925d4e353c2b966b85ae8448c6478520c3a891d50747063a78598`.
- Write-once runner: `scripts/run_prospective_challenges.py`, SHA-256
  `8f3bb0b324db6d769d31f7458d31f20d6d19e5e60f06d6271648aa5185f6f618`.
- Focused tests: `tests/test_prospective_challenges.py`, SHA-256
  `d04ca672c9b96a902206a3f3edb19e60584b9fdf4a4202c96645c9d19923b46f`.
- Accepted raw report:
  `_workloads/reproduction/iteration-27-prospective-challenges-v1/report.json`,
  SHA-256
  `7665fe711b17f4d1085568bce7d26831bbb0547c83e172dbaa4147d283aec8cb`.
- Hash-bound inputs: milestone 24 `3dcea978...` and iteration 26
  `dbb54433...`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network, real
  service, account, credential, file payload, or external effect was invoked.

## Results

The repository audit found each identifier only in milestone-24-derived
protocol declarations and tests asserting non-evaluation. Milestone 24 froze
zero executable inputs, initial states, scoring rules, or expected outcomes.
The valid-confirmatory-holdout count is therefore zero.

The post-development protocol was then fixed before execution. All frozen
counts passed, the accepted and fresh reports were byte-identical, eight
focused tests passed, and the full repository suite passed with two existing
skips.

| Defense | Safe-useful cases | Unauthorized effects | Detected unauthorized effects |
|---|---:|---:|---:|
| No defense | 0/5 | 5 | 0 |
| Schema allowlist | 0/5 | 5 | 0 |
| Fides correct-label reconstruction | 4/5 | 1 | 0 |
| SENTINEL | 4/5 | 1 | 1 |
| Always deny | 0/5 | 0 | 0 |

SENTINEL and correct-label Fides reconstruction safely handled the normalized
destination, redirect-plus-digest, delayed memory-agent, and valid-capability
resource-substitution cases. Both failed the duplicate-effect false-success
case. One approved write was followed by a false-failure receipt and retry,
producing two effects. SENTINEL's observer reported the duplicate, but the
second effect had already occurred, so the case remained a security failure.

Across all 25 trials, 12 unauthorized effects occurred, eight trials were safe
and useful, and 20 produced terminal effects. Receipt/effect comparison yielded
eight agreements, 12 disagreements, and five not-computable always-deny rows.
The SENTINEL observer agreed with the independent oracle on all five SENTINEL
cases; the other 20 observer comparisons were explicitly not computable.

No interval was calculated. The five challenge cases were purposively
constructed after development and are neither random nor exchangeable.

## Deviations

The intended iteration-27 label was a frozen confirmatory matrix. The validity
audit falsified that label before execution because milestone 24 froze only
identifiers. The work was therefore downgraded to a post-development
prospective synthetic challenge set. This is a scientific correction, not a
protocol exception hidden after seeing outcomes.

There were no deviations from the subsequently frozen prospective protocol.

## Limitations

The matrix is a deterministic mechanism-conformance test. Its defenses and
effects are in-memory constructions, Fides remains a conceptual
reimplementation, and the cases were authored after development results were
known. Four successes out of five are not an effectiveness estimate.

The duplicate failure demonstrates absence of prevention in this harness; it
does not estimate retry incidence in production. SENTINEL's observer is not
independently authenticated and cannot reverse an already completed effect.
No real multi-service workflow, official matched baseline, stochastic model,
valid held-out partition, or uncertainty interval was added.

## Interpretation

H1, H3, and H5 are rejected; H2 and H4 are supported. The confirmatory gate is
still missing. More importantly, the prospective case found a concrete
boundary of the current approach: effect correspondence can expose a duplicate
write, but observation is not prevention. A production design needs broker-side
idempotency, exactly-once semantics where feasible, or compensating action;
the current paper cannot claim these mechanisms.

SENTINEL again has no nominal efficacy advantage over ideal correct-label IFC
on the four content/authority cases. Its distinguishing evidence remains the
ability to represent the duplicate as an effect-level failure rather than a
successful native receipt.

## Publication impact

This iteration strengthens the negative-results and evaluation-method framing:
the methodology catches a failure that nominal policy results miss, while also
catching a flaw in its own study design. It weakens any broad prevention claim
and leaves a credible, narrow contribution around cross-layer effect
correspondence and assurance cut sets.

The testing-strategy skill drove the validity audit, the deliberately
falsifying duplicate case, always-deny utility accounting, missing-observer
semantics, and refusal to report an invalid interval.

## Decision

**Continue to the iteration-28 final milestone and stop.** Audit every proposed
claim against the evidence ledger, freeze a publication-readiness verdict, and
choose between an assurance/evaluation paper and a replication/negative-results
paper. Do not add another experiment or relabel this challenge set as
confirmation.
