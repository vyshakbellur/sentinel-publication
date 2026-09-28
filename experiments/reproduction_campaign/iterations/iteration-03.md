# Iteration 03: validate AgentDojo tasks, attacks, and scorers

Timestamp: 2026-09-28T20:23:00Z

## Research question

Do AgentDojo v1.1.2's native ground-truth task execution, injection reachability
check, attack-vector selection, and utility/attack-goal scorers agree on a
model-free smoke study?

## Competing explanations

- H1: the released suite validator, ground-truth executions, and scorers agree
  for every native task.
- H2: the task and scorer substrate is sound, but a validator or representation
  conversion has regressed.
- H3: native task ground truths or effect-based scorers fail, preventing a
  meaningful baseline experiment.

## Smallest discriminating action

At pinned AgentDojo source revision `089ed468`, run the released v1.1.2 suite
checker both with and without its injectability check. Independently repeat the
injectability calculation with the package's canonical
`get_text_content_as_str` converter, and execute one deterministic benign and
one deterministic attacker ground-truth path for each of the four suites.

## Acceptance and falsification criteria

- Ground-truth validity requires every native user and injection task to pass
  the released utility or attack-goal scorer.
- Injectability agreement requires the released checker and a representation-
  aware checker to identify the same reachable tasks.
- For each stratified scorer sanity pair, the user ground truth must yield
  utility true and attack goal false, while the injection ground truth must
  yield utility false and attack goal true.
- H1 is falsified by any checker disagreement. H3 is supported by a failed
  ground-truth or scorer sanity condition.

## Exact artifacts and configuration

- AgentDojo commit: `089ed468cf3ed0322acc66b0211f26d9d90dbf60`.
- Benchmark version: `v1.1.2`.
- Source-snippet SHA-256 for `is_task_injectable`, lines 482--491:
  `8286356ce7a08fe36070b7d588b3ba224b2b5ca665a224669e630c321cba6f8c`.
- Interpreter/environment: iteration 2's CPython 3.12.7 loose-dependency
  AgentDojo environment; therefore this is artifact validation, not exact
  locked-environment reproduction.
- Attack-vector sanity: released `DirectAttack`.
- Pair selection: the first registered user and injection task from each of
  workspace, travel, banking, and Slack.
- Raw evidence:
  `_workloads/reproduction/iteration-03-agentdojo-suite-checks/`.

## Results

1. With `--no-check-injectable`, all released ground-truth checks passed: 40
   workspace, 20 travel, 16 banking, and 21 Slack user tasks, plus all 6, 7, 9,
   and 5 respective injection tasks.
2. The default released checker reported every one of the 97 user tasks as
   "not injectable", reported all four suites failed, but still returned
   process exit code 0.
3. The representation-aware check found all 97 user tasks injectable. Every
   one of the 339 inspected tool responses stored `content` as a list of typed
   blocks. The released `is_task_injectable` comprehension calls the canonical
   converter only when `content` is a `str`; consequently it discards every
   current tool response and searches an empty string.
4. The released `DirectAttack.get_injection_candidates`, which already uses the
   canonical converter without that type filter, selected one reachable vector
   for each stratified task.
5. All four scorer sanity pairs behaved as discriminated: a user ground-truth
   execution scored `(utility=true, attack_goal_achieved=false)`, and an
   injection ground-truth execution scored
   `(utility=false, attack_goal_achieved=true)`.

## Deviations

- The initial wrapper completed the default suite check but then hit zsh's
  read-only `status` variable while recording its exit code. Its output was
  preserved. A write-once rerun using `run_status` confirmed the checker exits
  zero even when all suites are printed as failed.
- An initial scorer script imported a nonexistent attack class and produced an
  empty output file. The failure was preserved; the `DirectAttack` rerun is the
  reported result.
- No probabilistic model or paper-reported benchmark condition was executed.

## Limitations

The corrected reachability calculation was an independent diagnostic, not an
upstream patch. Only one task/injection pair per suite received the two-sided
scorer sanity execution, although all 97 user and 27 injection ground truths
passed their released checks. The loose dependency environment remains a
fidelity limitation.

## Interpretation

H1 and H3 are rejected; H2 is supported. The core v1.1.2 task ground truths,
attack candidate discovery, and sampled scorers are internally usable, but the
released default suite-validation gate has a message-representation regression
and does not signal failure via its process status. This defect does not prove
that published benchmark scores are wrong, because normal per-task attack
candidate discovery uses a different, representation-aware path. It does show
that a nominally successful validation command is not adequate evidence.

AgentDojo also names the second result `security` while the task contract and
observed sanity checks use true to mean that the attack goal was achieved. The
common study will retain the native field but add the explicit alias
`attack_goal_achieved` to prevent directionality errors.

## Publication impact

This is a concrete benchmark-validity finding suitable for the study's
reproducibility section and motivates independent effect oracles without
overclaiming a defense result. The confirmatory harness must fail closed on
validation disagreement and must not rely on command exit status alone. The
finding also reinforces the paper's separation between an agent/framework
verdict and independently observed effects.

## Decision

**Continue.** Iteration 4 should freeze a development subset only after adding
a version-pinned representation-aware validation gate, then conduct the first
formal milestone review. No paper efficacy number has yet been reproduced.
