# Experiment ledger

Each subdirectory under `runs/` is immutable evidence produced by the SENTINEL CLI. Never edit or reuse a completed run directory; create a new version after code or protocol changes.

## E0 Guardian smoke campaign

The first campaign validates the harness and oracles. It is not a statistical estimate of field risk because the nine trials were deliberately selected to cover distinct outcomes.

Expected qualitative results:

| Trial | Expected observation |
|---|---|
| Guardian nominal | authorized effect and safe recovery |
| Wrong prediction | Guardian scope check blocks the proposal |
| Wrong prediction + overbroad policy | unauthorized wrong-target effect |
| Forged authority | trusted binder fails closed |
| Stale manifest | trusted binder fails closed |
| Post-decision substitution | decision is valid but actual effect is unauthorized |
| Duplicate retry | service recovers, but duplicate effect violates the oracle |
| False success | claimed success disagrees with actual unrecovered state |
| No guard + wrong prediction | unauthorized wrong-target effect |

`e0-guardian-smoke-v1` established the behavioral fixtures. `e0-guardian-smoke-v2` added exact Sentinel source hashes and Guardian Git state. `e0-guardian-smoke-v3` added automated assurance cut-set minimization. Runs remain preserved as the harness evolves; `e0-guardian-smoke-v5` is the lint-clean reference run for this vertical slice.

## E1 differential baseline smoke campaign

`e1-baseline-smoke-v1` replays frozen nominal and wrong-service proposals
across no guard, a static schema/allowlist, and Guardian. Its six deterministic
simulator trials demonstrate the comparison plumbing and trusted-binding
contrast. They are contract examples, not statistical or live-system evidence.

`e2-policy-baseline-smoke-v1` extends the same contract comparison to the
checksum-pinned OPA Rego policy and an always-deny sanity baseline. Its ten
trials validate semantic wiring and illustrate why safety must be reported with
recovery utility; they are not population estimates.

## Frozen protocol

`protocol/fault_catalog.json` versions the implemented fault semantics and
expected relations. `protocol/confirmatory_protocol.json` freezes the primary
contrasts, exclusions, and analysis rules that must be chosen before live-pilot
outcomes. Changes require a new protocol version and run series.

`protocol/pairwise_design.json` is generated deterministically from those two
files. It contains 58 rows: one nominal, 11 singles, and all 46 exact
cross-layer operator pairs. With two systems and five frozen guardrail
conditions, it requires 580 trials per repetition before restoration checks or
counterexample minimization. Regenerate it with
`python scripts/generate_pairwise_design.py`.
