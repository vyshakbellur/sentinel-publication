# SENTINEL 28-iteration reproduction campaign

Started: 2026-09-28

## Objective

Determine whether SENTINEL supports a publication-worthy contribution beyond
existing agent defenses. The acceptable outcomes are a positive mechanisms
paper, an assurance/evaluation paper, or an informative replication and
negative-results paper.

## Hard bounds

- Stop after at most 28 substantive iterations.
- A timer/status poll is not an iteration.
- Do not overlap experiments that share mutable state or compute services.
- Default heartbeat is ten minutes. A running experiment may set its next
  useful inspection to 20 or 30 minutes without being restarted.
- Use public or synthetic data and inert security fixtures only.
- Do not use paid APIs without a separately recorded user-authorized budget.
- Do not tune on the confirmatory partition.
- Every iteration ends in `continue`, `pivot`, `repeat`, or `stop`.

## Evidence required per iteration

Each numbered record must contain the research question, competing
explanations, smallest discriminating test, acceptance and falsification
criteria, exact versions/configuration, raw-result locations, results,
deviations, limitations, interpretation, publication impact, and next decision.

## Planned gates

The plan is adaptive: later work changes when earlier evidence falsifies an
assumption. Milestone reviews occur at 4, 8, 12, 16, 20, 24, and 28.

| Iteration | Intended decision |
|---:|---|
| 1 | Freeze artifact identities and grade exact reproducibility. |
| 2 | Build isolated baseline environments and dependency/license audit. |
| 3 | Validate AgentDojo native tasks, attacks, and scorers on a smoke subset. |
| 4 | Review benchmark validity and freeze the development subset. |
| 5 | Reproduce a CaMeL smoke condition. |
| 6 | Run matched CaMeL/no-defense/built-in-defense trials. |
| 7 | Probe CaMeL policy, provenance, and binding assumptions. |
| 8 | Review whether trusted attribute binding remains a gap. |
| 9 | Install and smoke-test the pinned Agent-C Zenodo artifact. |
| 10 | Reproduce benign temporal-task trends. |
| 11 | Reproduce adversarial temporal conformance trends. |
| 12 | Review temporal enforcement versus resource/identity binding. |
| 13 | Execute and characterize the Fides tutorial artifact. |
| 14 | Reconstruct a minimal matched Fides/AgentDojo condition. |
| 15 | Implement and validate a minimal ToolGate-style contract baseline. |
| 16 | Review baseline fidelity and eliminate unsupported novelty claims. |
| 17 | Define a common action/effect trace interface without changing native scorers. |
| 18 | Add independent environment-effect oracles and disagreement metrics. |
| 19 | Test identity, tenant, resource, destination, provenance, and delegation substitution. |
| 20 | Review evidence for trusted attribute binding and effect-grounded assurance. |
| 21 | Implement the synthetic calendar promptware environment and benign hard negatives. |
| 22 | Implement non-transitive URL/file resource transitions with inert fixtures. |
| 23 | Reconstruct covered Invitation scenarios and compare defense families. |
| 24 | Review scenario fidelity, utility, and containment claims. |
| 25 | Run frozen adaptive attacks against the development-selected defenses. |
| 26 | Run cross-layer boundary faults and minimize assurance cut sets. |
| 27 | Run the frozen confirmatory matrix and statistical analysis. |
| 28 | Audit claims against evidence and choose the final paper framing. |

## Stop and pivot rules

- If a published system already jointly covers a candidate contribution, drop
  that novelty claim.
- If a baseline cannot be executed, document why and use a clearly labeled
  reconstruction; do not invent a reproduced number.
- If static attacks saturate, move to adaptive attacks rather than tuning a
  detector to the static corpus.
- If independent effect observation does not change any conclusion, remove it
  from the claimed contribution.
- If SENTINEL cannot beat always-deny-normalized utility, it has not shown a
  useful security boundary.
- If no positive mechanism result survives, prepare the replication and
  negative-results framing.

