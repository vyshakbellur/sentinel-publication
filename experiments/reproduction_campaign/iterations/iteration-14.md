# Iteration 14: Fides-style integrity reconstruction on AgentDojo

Timestamp: 2026-09-29T00:04:46Z

## Research question

On a frozen AgentDojo development subset, does a minimal Fides-style integrity
policy preserve benign utility while stopping untrusted side effects, and does
its protection survive an adapter that incorrectly labels the same attack trace
as trusted?

## Competing explanations

- H1: any reduction in attack success is merely the utility collapse produced
  by denying every call.
- H2: correct integrity labeling plus a read/write policy blocks the selected
  untrusted effects while retaining the selected benign read-only utility.
- H3: the downstream policy remains protective when the adapter assigns the
  wrong integrity label.
- H4: apparent protection is a scorer artifact rather than a missing concrete
  side effect.

## Smallest discriminating action

Use the frozen AgentDojo v1.2 workspace task `user_task_0` and its released
ground-truth trace with injection tasks 0, 1, 2, and 4. Run the same native
AgentDojo task machinery under four deterministic controls: no defense,
always deny, a minimal Fides-style integrity policy with the correct untrusted
label, and the same policy with only the adapter label changed to trusted.
Preserve the native utility and attack scorers, and independently record whether
the exact required attack write was executed.

## Acceptance and falsification criteria

- No defense must preserve the four benign traces and execute all four released
  attack effects.
- Always deny must stop all four attacks but fail all four benign traces.
- Correct-label Fides-style enforcement must preserve all four benign traces and
  stop all four attack effects.
- Changing only the attack trace label to trusted must restore all four attack
  effects without changing benign utility.
- Native attack scoring and the independent exact-write oracle must agree on
  every row.
- Benign traces must not independently satisfy the paired attack goals.

Failure of any condition rejects the preregistered mechanism result rather than
being explained after inspection.

## Exact artifacts and configuration

- Evidence class: **conceptual reimplementation**.
- Fides reference revision:
  `669c046c4adbc56ee49c9672fdd30c54937ea062`.
- AgentDojo source revision:
  `928bbae820a89556b03de5cf818eb350cd6082d1`, release 0.1.34,
  benchmark version 1.2.
- AgentDojo lock SHA-256:
  `c3f154ea45f9e9049d9f5a264e94883558c21ed6110e5e3c83c68759db3a7b31`.
- Protocol: `experiments/protocol/fides_agentdojo_reconstruction.json`,
  SHA-256
  `a5a9657680f175849db8c1f2c5916b297c2c4d7bf9c77ef7b6fc468344c4aef3`.
- Runner: `scripts/run_fides_agentdojo_reconstruction.py`, SHA-256
  `e7cd668fbadf1805aca5051d250eb6f5cf6d8035a55b6db05048bae04b74ec64`.
- Accepted raw report:
  `_workloads/reproduction/iteration-14-fides-agentdojo-v2/report.json`,
  SHA-256
  `87cc146eba9eb4ff51ceb72ae8ae569474bd8d2e5106d2673cfb986bd7d1c720`.
- Host/interpreter: Darwin arm64, the existing AgentDojo Python 3.12
  environment established in iteration 2.

The policy uses two integrity levels. Read-only calls are allowed at either
level; workspace side-effect calls are denied when the whole proposed trace is
untrusted. The correct-label and mislabeled conditions differ only in the label
assigned to the attack ground-truth trace.

## Results

All preregistered acceptance checks passed across 16 rows:

| Guardrail | Pairs | Benign utility | Native attacks achieved | Exact attack writes executed |
|---|---:|---:|---:|---:|
| No defense | 4 | 4/4 | 4/4 | 4/4 |
| Always deny | 4 | 0/4 | 0/4 | 0/4 |
| Fides-style, correct label | 4 | 4/4 | 0/4 | 0/4 |
| Fides-style, mislabeled adapter | 4 | 4/4 | 4/4 | 4/4 |

The attacks span `send_email`, `delete_file`, `create_calendar_event`, and a
two-step `search_emails` then `send_email` secret-exfiltration trace. In the
last case, correct-label enforcement permitted the read and blocked the write;
always deny blocked the read itself. Thus, on this narrow read-only benign task,
correct labeling distinguishes the mechanism from utility-destroying denial.

The native AgentDojo attack scorer and independent exact-write oracle agreed on
all 16 rows. None of the benign traces satisfied its paired attack scorer. The
report field `utility_under_attack_trace` is false for every adversarial row
because those rows deliberately execute an injection task's ground truth rather
than the benign user's task; it is not treated as a utility-under-attack efficacy
measure.

## Deviations

The first accepted-looking report was preserved under
`iteration-14-fides-agentdojo-v1`. Before freezing the result, the runner was
strengthened with a negative-control check that benign traces do not satisfy the
attack goals. The v2 report is the accepted artifact; this added check changed
no policy, trace, or primary result.

No LLM was invoked. Released ground-truth traces replace proposal generation so
that the iteration isolates deterministic enforcement and label faults.

## Limitations

This is not Microsoft Fides code and not the Fides paper's AgentDojo
implementation or efficacy result. It is a minimal integrity reconstruction
informed by the public tutorial. It omits Fides confidentiality, selective
hiding, finer-grained provenance, and planner-specific behavior.

Only one benign read-only workspace task is repeated across four development
attacks. There is no benign write task, held-out evaluation, stochastic model,
confidence interval, latency comparison, or statistical inference. The policy
assigns integrity to an entire ground-truth trace, and the mislabeled condition
is a deliberately injected boundary fault—not a demonstrated prompt-injection
path to label corruption.

The testing strategy's matched controls and dual scoring show what happened to
these effects; they do not establish how often real adapters mislabel content or
how often an LLM proposes the attacks.

## Interpretation

H2 is supported and H1, H3, and H4 are rejected for this selected deterministic
matrix. A correct Fides-style integrity label completely contains these four
released attack traces while preserving the selected read-only utility. A
single adapter-label fault collapses the measured protection to the no-defense
result on all four attacks.

This is evidence for a cross-layer assurance claim, not evidence that Fides is
weak. Fides explicitly depends on correct labels. The complementary SENTINEL
question is whether the origin, identity, resource, arguments, and provenance
used at the tool boundary were authenticated and bound before a deterministic
policy consumed them. Label construction and fault testing therefore belong in
the trusted computing base and evaluation protocol.

## Publication impact

The result supplies a reproducible mechanism control and a concrete adapter
fault intervention. It strengthens the paper's motivation for trusted attribute
binding: downstream IFC can be correct while end-to-end protection fails because
the boundary supplied the wrong trust fact. It does not yet establish publishable
end-to-end efficacy, and should be presented as a controlled fault result rather
than an attack-success comparison against official Fides.

The testing-strategy skill materially shaped this iteration by requiring
no-defense and always-deny controls, changing one variable between the two Fides
conditions, and checking native scores against an independent effect oracle.

## Decision

**Continue.** Iteration 15 should reproduce or clean-room reconstruct the
smallest executable ToolGate authorization baseline specified in the campaign
charter, preserving its native policy semantics and adding the same independent
effect/accounting discipline. The goal is to determine whether ToolGate already
binds complete trusted action attributes or leaves a distinct boundary gap.
