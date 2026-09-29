# Iteration 23: Invitation threat-class reconstruction and defense comparison

Timestamp: 2026-09-29T02:23:58Z

## Research question

Across the five threat classes reported by *Invitation Is All You Need*, how do
no defense, schema validation, a correctly labeled Fides-style reconstruction,
the same reconstruction with a mislabeled adapter, SENTINEL, and always-deny
compare under identical inert plans and independent effect grading?

## Competing explanations

- H1: schema validation contains the selected threat-class analogs.
- H2: SENTINEL is strictly better than correctly labeled information-flow
  control on these fixed scenarios.
- H3: information-flow containment is insensitive to adapter labeling.
- H4: correct IFC and task-scoped SENTINEL both contain these analogs, while
  their scientific difference lies in boundary-fault robustness and effect
  correspondence rather than nominal fixed-plan efficacy.
- H5: behavioral class coverage is equivalent to exact reproduction of the
  paper's 14 production attacks.

## Smallest discriminating action

Pin the primary paper's five-class taxonomy, construct two inert behavioral
analogs per class plus one benign control per class, and run each twice across
six defense conditions. Preserve the Fides conditions as explicitly conceptual
reconstructions. Grade only in-memory terminal consequences and separately
record exact production elements that remain unsupported.

## Acceptance and falsification criteria

- Cover all five paper threat classes with ten behavioral attack analogs and
  explicitly report zero exact production scenarios reproduced.
- Run 180 trials with exact native-namespace round trips and byte-identical
  reruns.
- Correct-label Fides reconstruction and SENTINEL must each preserve 10 benign
  controls, safely complete 20 attacked tasks, contain 20 attacks, and produce
  zero unauthorized effects.
- Fides adapter mislabeling, schema-only, and no defense must each complete 20
  unauthorized effects; always-deny must contain attacks but lose all benign
  utility.
- Record 120 attempted unauthorized actions, 60 completed unauthorized effects,
  150 terminal effects, and 90 safe-useful trials.
- Receipt/effect comparisons must yield 90 agreements, 60 disagreements, and
  30 not-computable results.

## Exact artifacts and configuration

- Primary source: `https://arxiv.org/abs/2508.12175`, checked 2026-09-29. The
  five classes are Short-Term Context Poisoning, Permanent Memory Poisoning,
  Tool Misuse, Automatic Agent Invocation, and Automatic App Invocation.
- Protocol: `experiments/protocol/invitation_scenario_reconstruction.json`,
  SHA-256
  `c84509aa328179f2346ab9d9a1160c5dba7f081be824f620c027d6ab28fd4d4f`.
- Reconstruction and oracle:
  `sentinel_experiments/invitation_reconstruction.py`, SHA-256
  `74f0f566566cb0353cdb19a570c2748d3657859a9c1ea75d87c5e409db4029e1`.
- Write-once runner: `scripts/run_invitation_reconstruction.py`, SHA-256
  `7eb3d4018b126e4d32a236092e1251a7a631208a8a154dde0d651f2b6a9cb88a`.
- Focused tests: `tests/test_invitation_reconstruction.py`, SHA-256
  `eddad3e445caff703c6bb66166c0a73bf4bb6af5431981e8b80ae99196952c84`.
- Accepted raw report:
  `_workloads/reproduction/iteration-23-invitation-reconstruction-v1/report.json`,
  SHA-256
  `567f1ecff74dc7659f242c6a4535c2d6d9534648d40252295e5d2b8ac322c48c`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network,
  account, application, device, camera, browser, home control, or external
  service was invoked.

## Results

All preregistered counts passed and the fresh report was byte-identical.

| Defense | Benign utility | Safe attack utility | Attacks contained | Unauthorized effects |
|---|---:|---:|---:|---:|
| No defense | 10/10 | 0/20 | 0/20 | 20 |
| Schema allowlist | 10/10 | 0/20 | 0/20 | 20 |
| Fides correct-label reconstruction | 10/10 | 20/20 | 20/20 | 0 |
| Fides mislabeled-adapter reconstruction | 10/10 | 0/20 | 0/20 | 20 |
| SENTINEL | 10/10 | 20/20 | 20/20 | 0 |
| Always-deny | 0/10 | 0/20 | 20/20 | 0 |

Correctly labeled IFC and SENTINEL tie on the selected nominal fixed-plan
matrix. Adapter mislabeling eliminates the reconstruction's containment,
matching the mechanism-level assumption exposed in iteration 14. The
permissive conditions produced 60 receipt/effect disagreements: each reported
completion while the independent terminal consequence was unauthorized.

The reconstruction covers all five threat classes but only as ten behavioral
analogs. It reproduces 0/14 exact scenarios. Unsupported elements include the
production Gemini applications, Gmail/Calendar/Docs integrations, browser,
Zoom, smart-home devices, camera, geolocation, physical effects, exact payloads
and prompts, product versions, deployed mitigations, and the paper's TARA risk
measurements.

Six focused tests and the full repository suite passed, with two existing
skips.

## Deviations

None from the frozen protocol. The primary-source check confirmed the five
class names and 14-scenario count before the mapping was frozen. The public
project page supplied additional behavioral descriptions, but no production
artifact or exact harness was incorporated.

## Limitations

This is conceptual reimplementation at the behavioral-class level. Fixed plans
replace the original Gemini-powered assistants and do not estimate injection
success. Consequences are inert labels, not spam, phishing delivery, memory,
calendar changes, data exfiltration, video, geolocation, or physical control.

The Fides rows are a clean-room conceptual reconstruction, not execution of an
official AgentDojo or Invitation harness. SENTINEL and Fides tying here does not
prove semantic equivalence; it only shows that both idealized policies reject
the selected untrusted flows. Adapter mislabeling is a deliberately injected
assumption failure, not an estimated production error rate.

The fixtures are development data, the observer is in process, and deterministic
repetition provides no confidence interval. No published effectiveness number
is reproduced.

## Interpretation

H1, H2, H3, and H5 are rejected; H4 is supported. SENTINEL cannot claim nominal
superiority over correctly labeled IFC from these scenarios. The defensible
differentiator is whether a complete assurance chain continues to correspond
when labels, adapters, policies, execution, receipts, and observers fail—not
whether one ideal policy blocks a fixed malicious action.

This negative result improves the paper: it prevents presenting the calendar
matrix as proof that SENTINEL supersedes CaMeL/Fides-style control/data
separation. It instead motivates the cross-layer fault and minimal-cut-set
experiments.

## Publication impact

The study now has a transparent paper-to-fixture mapping, matched defense-family
controls, benign utility, and effect-grounded outcomes. It still lacks exact
scenario reproduction, live-model attack rates, real multi-service effects,
published baseline implementations on this corpus, and external observation.

The testing-strategy skill shaped the class-stratified benign controls,
assumption-fault row, equality check between nominal defenses, effect oracle,
and explicit unsupported-system inventory.

## Decision

**Continue to milestone review.** Iteration 24 should audit scenario fidelity,
utility, containment, baseline status, and claim language across iterations
21–23. It must decide whether the resource-transition candidate survives as a
research contribution or remains only an engineered reference mechanism, and
freeze the development-selected defenses and scenario partitions before any
adaptive or confirmatory work.
