# Iteration 24 milestone: scenario fidelity and development freeze

Timestamp: 2026-09-29T02:37:07Z

## Research question

Do iterations 21–23 provide publication-grade scenario, baseline, effect, and
statistical evidence, and which claims and development selections should be
frozen before adaptive attacks and confirmatory evaluation?

## Competing explanations

- H1: perfect deterministic containment in the selected synthetic matrices is
  sufficient for publication.
- H2: class-level Invitation coverage is equivalent to exact reproduction.
- H3: non-transitive resource transitions are a novel mechanism established by
  metadata simulation.
- H4: the results are useful development evidence, but the main surviving
  contribution is cross-layer effect correspondence and fault assurance.
- H5: SENTINEL has demonstrated nominal superiority over correctly labeled IFC.

## Smallest discriminating action

Freeze a hash-bound audit over milestone 20 and the accepted calendar,
resource-transition, and Invitation reconstruction reports. Apply explicit
fidelity rules for exact reproduction, official baselines, real effects,
statistics, and nominal superiority. Aggregate only compatible development
counts, then freeze adaptive defenses, mutation operators, attempt budget,
boundary-fault variants, and confirmatory holdout identifiers before outcomes
are inspected.

## Acceptance and falsification criteria

- Verify all four source hashes and reproduce the audit byte-for-byte.
- Aggregate 444 development trials, 128 completed unauthorized effects, and 128
  receipt/effect disagreements without promoting them to production rates.
- Confirm SENTINEL development utility of 42 benign and 54 attacked tasks with
  zero unauthorized effects, while recording 42 always-deny benign failures.
- Preserve five-class behavioral coverage but record 0/14 exact Invitation
  scenarios reproduced.
- Reject nominal superiority if correct-label Fides reconstruction ties
  SENTINEL on the matched matrix.
- Downgrade resource transitions to an engineered experimental factor unless
  real system or prior-art-comparative evidence exists.
- Publication readiness requires all seven gates; any missing gate falsifies
  readiness.

## Exact artifacts and configuration

- Protocol and development freeze:
  `experiments/protocol/milestone24_fidelity_audit.json`, SHA-256
  `7e11944b674f1eaf07ba3a7196ddc60063646755b9f2e0fec24ed3d4eb09cb6e`.
- Audit implementation: `scripts/audit_milestone24_fidelity.py`, SHA-256
  `a158b00abc56b7243308ceb5a44601db842e14b9b81b5f25e3e1049ff856562f`.
- Accepted raw report:
  `_workloads/reproduction/iteration-24-fidelity-audit-v1/report.json`, SHA-256
  `3dcea978772f3f2c5287b86e82e7973994e142b6a96e42f38e8d3916adb2baf0`.
- Verified input reports: milestone 20 `d5bc56b8...`, calendar iteration 21
  `aaeeece3...`, resources iteration 22 `a381c969...`, and Invitation
  iteration 23 `567f1ecf...`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network,
  external application, or effect was invoked.

## Results

The audit passed and reproduced byte-for-byte.

| Evidence property | Milestone-24 finding |
|---|---|
| Development trials | 444 deterministic synthetic trials |
| Completed unauthorized effects | 128 in permissive controls |
| Receipt/effect disagreements | 128 |
| SENTINEL benign utility | 42 |
| SENTINEL safe attack utility | 54 |
| SENTINEL unauthorized effects | 0 |
| Always-deny false benign denials | 42 |
| Invitation class coverage | 5/5 behavioral classes |
| Exact Invitation scenarios | 0/14 |

The claim decisions are:

- retain cross-layer effect correspondence as the primary evaluation
  candidate;
- retain trusted complete-tuple construction as a reference mechanism;
- retain non-transitive resource transitions only as an engineered
  experimental factor, not a novel mechanism;
- retain Invitation results as conceptual development evidence only;
- reject nominal superiority over correctly labeled IFC on the selected
  matrix; and
- require minimal assurance cut sets as the next differentiating experiment.

All seven publication gates remain missing: matched official published
baselines, held-out confirmatory results, probabilistic repeated seeds,
uncertainty intervals, realistic multi-service effects, independently
authenticated observation, and adaptive attack results.

The audit freezes five adaptive conditions—no defense, schema allowlist,
correct-label Fides reconstruction, SENTINEL, and always-deny—plus seven
development mutation operators and a 12-attempt budget per seed. Adapter,
broker, and observer faults are reserved for iteration 26. Five confirmatory
holdout identifiers are frozen without outcome inspection.

## Deviations

None from the frozen protocol. The confirmatory holdout entries are identifiers
and scenario descriptions only; no implementation or expected result was
created in this iteration.

## Limitations

The aggregate counts combine distinct synthetic matrices and are descriptive,
not pooled effect-size estimates. No independence assumption or confidence
interval applies. Correct-label Fides remains conceptual, while the remaining
controls are local. The resource state machine is metadata-only. Effect sinks
are in process. The five holdout identifiers alone do not constitute a valid
confirmatory dataset.

The audit does not solve the absence of a reliable probabilistic planner. A
weak local model result would still be uninterpretable as defense efficacy.
Iteration 25 must therefore use a deterministic adaptive attacker over the
development partition and report its scope honestly.

## Interpretation

H1, H2, H3, and H5 are rejected; H4 is supported. The selected systems results
show that the reference mechanisms behave as designed and that native success
can disagree with safe effects. They do not establish production efficacy or a
novel URL/file security model.

The remaining positive paper path is now narrow: an effect-grounded methodology
for testing how deterministic agent boundaries fail across layers, including
trusted attribute construction, execution correspondence, and minimal fault
sets. The negative-results path remains equally credible: nominal deterministic
defenses can tie under ideal assumptions, while their public artifacts and
native metrics do not jointly establish end-to-end assurance.

## Publication impact

Milestone 24 prevents synthetic saturation from becoming an inflated claim and
locks the development choices before adaptive tuning. The paper is still not
ready for arXiv. Iterations 25–27 are now the critical path: adaptive
development attacks, assurance cut sets, and a frozen confirmatory analysis.

## Decision

**Continue with the frozen development plan.** Iteration 25 should execute a
deterministic adaptive attacker over development fixtures only, using the seven
frozen mutation operators and 12-attempt budget per seed. It must not inspect
the five confirmatory holdouts, and it must separate attacks on the agent input
from faults in the trusted boundary reserved for iteration 26.
