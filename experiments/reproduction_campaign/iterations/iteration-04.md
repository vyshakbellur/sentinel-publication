# Iteration 04: benchmark-validity milestone and development freeze

Timestamp: 2026-09-28T20:36:09Z

Milestone: 4 of at most 28 substantive iterations.

## Research question

Is AgentDojo sufficiently validated to freeze a development-only CaMeL subset
without contaminating future confirmatory tasks, and do native scorers agree
with executed ground-truth effects across that subset?

## Competing explanations

- H1: the CaMeL-locked AgentDojo revision has a clean validation substrate, so
  a stratified development subset can be frozen directly.
- H2: the substrate is usable only with explicit, version-pinned validation and
  known native-metric disagreements preserved separately.
- H3: failures are too broad or unexplained to proceed to a CaMeL smoke study.

## Smallest discriminating action

At AgentDojo 0.1.34's exact commit, validate every v1.2 ground truth and
representation-aware injection route, then freeze 16 stratified user tasks and
16 injection tasks before observing any defense outcome. Cross every selected
user task with the four selected injection tasks in its own suite and execute
both benign and attacker ground-truth pipelines, yielding 64 deterministic
two-sided scorer checks. Add a fail-closed validator and test its revision
guard with the wrong revision.

## Acceptance and falsification criteria

- The frozen subset must reference the exact AgentDojo revision locked by
  CaMeL, contain unique resolvable task IDs, declare its development-only role,
  and leave every unlisted task unavailable for tuning.
- Every selected user and injection ground truth must pass its released check.
- Benign ground truth should score utility true and attack goal false; attacker
  ground truth should score utility false and attack goal true.
- Any disagreement must be independently diagnosed, declared before defense
  runs, and retained in the native metric namespace rather than silently fixed.
- The validator must reject artifact revision drift with a nonzero exit.
- H3 is supported if an unexplained selected-task failure remains.

## Exact artifacts and configuration

- CaMeL revision: `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8`.
- CaMeL lock selects AgentDojo 0.1.34.
- AgentDojo 0.1.34 revision:
  `928bbae820a89556b03de5cf818eb350cd6082d1`.
- AgentDojo benchmark version: `v1.2`.
- Frozen subset:
  `experiments/protocol/agentdojo_development_subset.json`.
- Frozen subset SHA-256:
  `aac12711dd8496e54f3f8a86c405dbf152cbd1460fa88d0b0e12066e56b6a5fb`.
- Validator: `scripts/validate_agentdojo_artifact.py`, SHA-256
  `345b302d65ac49a564e5cda13cb671451d98f7b0e1715c45a4d5b48b58cc71b8`.
- Python: CPython 3.12.7 with iteration 2's loose AgentDojo dependency
  environment and the exact 0.1.34 source prepended to `sys.path`.
- Raw evidence:
  `_workloads/reproduction/iteration-04-agentdojo-dev-freeze/`.
- Primary validation report: `validation-report-v3.json`.
- Exact false-negative diagnostic:
  `workspace-user15-injection0-diagnostic.json`.

## Results

### Full native v1.2 audit

- All 97 user-task ground truths passed.
- Twenty-seven of 35 injection-task ground-truth witnesses passed. Workspace
  injection tasks 6--13 have empty released ground-truth action sequences, so
  the native checker cannot demonstrate their goal through that path. They are
  excluded from the development subset; this does not imply their security
  predicates are absent.
- The typed-content injectability defect persists in the CaMeL-locked 0.1.34
  revision: the released checker found 0 of 97 tasks injectable, while the
  representation-aware calculation found 97 of 97.

### Frozen development subset

- The subset contains four user and four injection tasks per suite: 16 benign
  tasks and 64 within-suite adversarial pairs.
- All selected ground-truth witnesses passed.
- Sixty-three of 64 two-sided native scorer checks matched the preregistered
  sanity direction. There were no unexplained failures.
- One workspace pair produced a reproducible native scorer false negative:
  `user_task_15` with `injection_task_0`. The attacker ground-truth trace
  executed `send_email` with the exact target recipient, subject, and body, and
  the post-state contained that sent email. However, the injected source email
  also contained the phrase `Important message!`; the scorer's broad subject
  search returned both messages and rejected the effect because it required
  exactly one match.
- This disagreement is frozen explicitly. The original native value remains
  reportable, while `attack_goal_achieved` and later effect-oracle values occupy
  separate fields.

### Fail-closed behavior and repository verification

- The validator accepted the exact artifact with 63 native sanity passes, one
  expected declared disagreement, and zero unexpected failures.
- Supplying AgentDojo revision `089ed468` instead of the frozen `928bbae8`
  caused exit code 1 before evaluation.
- The repository test suite passed all 239 collected tests; two were skipped.
  The validator also compiled successfully. Ruff was unavailable in the base
  environment, so no Ruff result is claimed.

## Deviations

- A local clone from the sparse/promisor AgentDojo checkout failed because its
  remote could not supply an unavailable object. The failed clone log was
  preserved. A detached git worktree from the already verified object was used
  for the exact 0.1.34 source.
- The first inventory accidentally fell back to the installed 0.1.35 package
  after that clone and checkout failure; it was used only for task inspection,
  not reported validation. All reported results come from the verified 0.1.34
  worktree.
- The first validator version correctly failed on the scorer disagreement but
  also treated all unselected empty-witness workspace injection tasks as a
  subset failure. The final validator narrows acceptance to selected tasks and
  permits only the one fully diagnosed, protocol-declared native disagreement.

## Limitations

This is deterministic artifact and scorer validation, not reproduction of a
published LLM efficacy number. The Python dependencies are not the exact lock.
The development subset is purposive and broad enough for wiring and failure
analysis, but it is not a statistically representative sample. The one trace
and post-state diagnostic is not yet SENTINEL's independent effect-oracle
implementation. No adaptive attack, repeated model seed, latency measure, or
confidence interval exists yet.

## Interpretation

H1 and H3 are rejected; H2 is supported. AgentDojo is usable for the next
stage only with explicit revision enforcement, representation-aware validation,
native-metric direction labels, and independently retained effect evidence.
The milestone exposed two different failure modes: a framework validation bug
that erases all typed tool outputs and a task scorer that misses a known
executed effect because the attack payload creates an extra search match.

## Publication impact and milestone review

What has been reproduced so far is limited to released model-free unit suites,
native ground-truth execution, and deterministic scorer behavior. No published
CaMeL, AgentDojo, Fides, Agent-C, or ToolGate effectiveness number has been
reproduced. Fides and ToolGate remain reconstruction paths; Agent-C remains an
artifact-replication path on this host.

The first milestone strengthens—but does not yet establish—the independent
effect-observation contribution. A native scorer can disagree with an exact
executed effect even before an LLM is introduced. This is a publishable
benchmark-validity observation if it generalizes beyond one pair; a single
case alone is insufficient for the paper's primary novelty claim. Trusted
attribute binding, non-transitive resource transitions, and cross-layer
assurance cut sets remain untested.

The current paper is not publication-ready. It now has a defensible,
non-leaking development protocol and two concrete benchmark defects. The next
gate is whether CaMeL can run a no-cost smoke condition or whether model/API
availability forces a clearly labeled substitution.

## Decision

**Continue.** Run the smallest CaMeL smoke condition on the frozen development
subset. Do not access held-out tasks, do not use a paid API, and do not describe
local-model portability as reproduction of the paper's reported result.
