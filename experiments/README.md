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
