# Iteration 25: deterministic adaptive promptware development search

Timestamp: 2026-09-29T02:53:42Z

## Research question

Does feedback-driven mutation of the ten development attack seeds evade the
frozen defense conditions within 12 attempts while preserving utility across
all mutated benign controls, and does this adaptive search distinguish
SENTINEL from correctly labeled Fides-style IFC?

## Competing explanations

- H1: superficial content mutation evades a schema allowlist but not a
  task-authority boundary.
- H2: the selected adaptive operators reveal a nominal efficacy difference
  between ideal correctly labeled IFC and SENTINEL.
- H3: attack containment is sufficient even if the defense loses benign
  utility.
- H4: the adaptive search validates the development harness but remains unable
  to discriminate ideal trusted-boundary mechanisms; the differentiating
  experiment must fault their assurance chains.
- H5: deterministic mutation counts can be interpreted as population attack
  rates.

## Smallest discriminating action

Freeze the five milestone-24 nominal defenses, seven mutation operators, ten
attack seeds, five benign seeds, and 12-attempt budget. For each attack seed,
feed the preceding native denial reason into the next deterministic mutation
and stop at the first independently observed unauthorized effect. Exercise all
12 variants for every benign seed regardless of outcome. Exclude the five
confirmatory holdouts and all adapter, broker, and observer faults.

## Acceptance and falsification criteria

- Execute 680 candidate trials with exact native-namespace round trips and a
  byte-identical fresh rerun.
- In the permissive controls, stop after one attempt per attack seed and
  observe 20/20 successful seeds and 20 unauthorized effects in total.
- In correct-label Fides reconstruction and SENTINEL, exhaust all 120 attack
  attempts per condition, preserve 60/60 mutated benign tasks, return 120/120
  safe useful attack dispositions, and observe zero unauthorized effects.
- Always-deny must contain every attack but fail all 60 benign variants.
- Record 480 receipt/effect agreements, 20 disagreements, and 180 explicitly
  not-computable comparisons.
- Generate no holdout trial and inject no trusted-boundary fault.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/adaptive_promptware_development.json`,
  SHA-256
  `b67741ce99b44d483201b519e44075cd254e43313d0d3f49283ab6dda5a4f984`.
- Adaptive harness and independent inert oracle:
  `sentinel_experiments/adaptive_promptware.py`, SHA-256
  `fd148c35cdea2c2353ccac98cb516ed75c8c38c2216b6049f4d6e802aad9b56b`.
- Write-once runner: `scripts/run_adaptive_promptware.py`, SHA-256
  `eafea2ae591b15a44f652759dfc3d584f213638b55914979d63e1fea3b09c5b7`.
- Focused tests: `tests/test_adaptive_promptware.py`, SHA-256
  `2705202a3d047ed8f8e784b753d825a6a7bb3b698eb21eda0a73ee027fb8c592`.
- Accepted raw report:
  `_workloads/reproduction/iteration-25-adaptive-promptware-v1/report.json`,
  SHA-256
  `f907098b06992617343f49b3efeace003429c304dcf7411e59ab284fb91015db`.
- Hash-bound source reports: milestone 24 `3dcea978...` and Invitation
  reconstruction `567f1ecf...`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network, account,
  application, file payload, or external effect was invoked.

## Results

All frozen counts passed, the fresh report was byte-identical, eight focused
tests passed, and the full repository suite passed with two existing skips.

| Defense | Attack attempts | Successful seeds | Benign utility | Safe attack utility | Unauthorized effects |
|---|---:|---:|---:|---:|---:|
| No defense | 10 | 10/10 | 60/60 | 0/10 | 10 |
| Schema allowlist | 10 | 10/10 | 60/60 | 0/10 | 10 |
| Fides correct-label reconstruction | 120 | 0/10 | 60/60 | 120/120 | 0 |
| SENTINEL | 120 | 0/10 | 60/60 | 120/120 | 0 |
| Always-deny | 120 | 0/10 | 0/60 | 0/120 | 0 |

The 680 trials comprised 380 attempted unauthorized actions, 500 terminal
effects, 480 safe-useful outcomes, and 20 unauthorized effects. Receipt/effect
comparison produced 480 agreements, 20 disagreements, and 180 not-computable
outcomes.

All seven operators were exercised, but their exposure counts are intentionally
unequal: permissive defenses succeeded on the first operator and stopped,
whereas contained attacks and benign controls traversed the full schedule.
Consequently, operator-level success comparisons are invalid in this design.

Correct-label Fides reconstruction and SENTINEL remained exactly tied. The
adaptive input mutations changed representation but not the typed action or
trusted-label premise, so they could not expose a difference between the two
idealized mechanisms.

## Deviations

The first runner command omitted the repository root from `PYTHONPATH` and
failed at import before reading the protocol or creating an output. The
accepted run used `PYTHONPATH=.`; no experimental condition or artifact was
changed. There were no deviations from the frozen protocol.

## Limitations

This is a deterministic state-machine search, not a learned attacker, live LLM
attack generation, or estimate of prompt-injection susceptibility. Mutation
operators are inert descriptors rather than transformed natural-language
payloads. Defense outcomes are mechanism rules, so the experiment validates
adaptive bookkeeping, stopping, utility accounting, and effect grading—not
empirical defense efficacy.

The Fides condition is still a conceptual reconstruction. Effects and the
observer remain in process. No official baseline, stochastic seed, uncertainty
interval, real multi-service effect, independently authenticated observer, or
confirmatory holdout was added. The deterministic adaptive result only
partially addresses the publication gate called `adaptive_attack_results`.

## Interpretation

H1 is supported only within the constructed mechanism rules; H2, H3, and H5
are rejected; H4 is supported. Content-level adaptive mutation does not create
a defensible SENTINEL superiority claim. This is a useful negative result: an
adaptive prompt corpus cannot establish end-to-end assurance when the key
scientific uncertainty is whether trusted labels, tuple construction,
dispatch, receipts, and observation remain aligned.

The most informative next experiment is therefore not another prompt mutation
round. It is a layer-by-layer boundary-fault matrix that measures the minimal
cut sets producing undetected unauthorized effects while holding the requested
action constant.

## Publication impact

Iteration 25 closes the adaptive development-harness task without inflating it
into a model-efficacy result. It strengthens a negative-results narrative and
prevents operator-count saturation from masquerading as robustness. The paper
is not ready for arXiv.

The testing-strategy skill shaped the explicit security-boundary, benign
utility, early-stopping, missing-evidence, and data-integrity checks.

## Decision

**Continue to iteration 26.** Execute only the four frozen boundary-fault
conditions, construct minimal assurance cut sets, and preserve identical
development actions and independent effect grading. Do not inspect the five
confirmatory holdouts until the cut-set design and interpretation are frozen.
