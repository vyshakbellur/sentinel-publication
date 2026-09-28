# Baseline reproduction study for trusted agent boundaries

Status: protocol draft based on an artifact audit performed 2026-09-28.

## Purpose

Before claiming that SENTINEL improves agent security, reproduce or reconstruct
the strongest relevant systems under a common threat model. The study must keep
three claims separate:

1. **Exact reproduction:** the authors' released code, data, model, prompts,
   parameters, and scorer are run at a pinned revision.
2. **Artifact replication:** released code is run with a documented substitute
   model or infrastructure component.
3. **Conceptual reimplementation:** the mechanism is independently implemented
   from the paper because a complete artifact is unavailable.

Only the first category may be described as reproducing a reported number.
Results from the other categories test portability or the stated mechanism.

## Initial 18-work screen

This is a deliberately mixed set of threat demonstrations, benchmarks,
detectors, and deterministic enforcement systems. A defense should not be
compared with an attack generator as if they were interchangeable baselines.

| Work | What its experiment gets right | Primary reported outcomes | Artifact status and SENTINEL question |
|---|---|---|---|
| [Invitation Is All You Need](https://arxiv.org/abs/2508.12175) | Demonstrates stored indirect injection through real calendar, mail, mobile, app, and home-agent surfaces; includes delayed triggers and lateral movement. | Fourteen scenarios across five threat classes; concrete digital and physical consequences. | No complete public harness found. The closed product has changed since disclosure. Reconstruct the scenarios in an isolated calendar environment; do not call this exact reproduction. Does authority remain confined when stored content crosses agents, apps, redirects, and time? |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Stateful environments, deterministic task/security checkers, benign utility and security under attack, and paired user/attacker tasks. | 97 user tasks and 629 security cases across workspace, travel, banking, and Slack. | Exact public benchmark. Use as the shared foundation for CaMeL, Fides, Task Shield, and firewall comparisons. Add independent effect receipts rather than replacing its native scorers. |
| [InjecAgent](https://github.com/uiuc-kang-lab/InjecAgent) | Broad tool-pair coverage and separation of direct harm from staged data stealing. | 1,054 cases, 17 user tools, 62 attacker tools; stage-specific and aggregate ASR. | Exact public dataset/harness. It lacks benign utility and utility-under-attack, so use it for attack-surface breadth, not as the sole security--utility result. |
| [Agent Security Bench](https://github.com/agiresearch/ASB) | Covers direct injection, observation injection, memory poisoning, and plan-of-thought backdoors across diverse domains. | Ten scenarios, more than 400 tools, 27 attack/defense methods, seven metrics. | Public artifact, but the forced-tool and scoring issues identified by later work must be corrected and reported alongside the original protocol. |
| [Are Firewalls All You Need?](https://arxiv.org/abs/2510.05244) | Re-evaluates four benchmarks, exposes benchmark bugs, reports BU/UA/ASR jointly, and adds semantic plus adaptive attacks. | Benign utility (BU), utility under attack (UA), ASR, latency, tokens, false positives/negatives, cross-model results. | Treat the Minimizer/Sanitizer as a mandatory strong probabilistic baseline. Its own finding that static benchmarks saturate motivates SENTINEL's effect-grounded and adaptive evaluation. |
| [AutoDojo](https://github.com/xhOwenMa/AutoDojo) | Optimizes attacks against the defense instead of replaying a fixed prompt set. | Adaptive ASR and defense degradation across AgentDojo defenses. | Public adaptive attacker. Use only on a development partition; freeze attacks before confirmatory evaluation and keep a held-out attacker/model. |
| [MUZZLE](https://github.com/gsiros/muzzle) | Uses live, resettable web applications, trajectory-selected injection surfaces, iterative payload refinement, and application-state assertions. | New attacks and adversarial objectives across multiple apps and browser-agent scaffolds. | Public artifact over The Zoo. Best browser/resource attacker for SENTINEL; augment its assertions with network, filesystem, credential, and process oracles. |
| [CaMeL](https://github.com/google-research/camel-prompt-injection) | Separates planning from untrusted-data interpretation, extracts a program before seeing tool data, tracks provenance, and applies capability policies. | Secure AgentDojo completion, utility degradation, token/runtime costs. | Official reproducibility artifact; inspected revision `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8`. First exact deterministic baseline. Test policy omissions, provenance loss, alternate routes, redirects, stale bindings, and post-authorization argument changes. |
| [Fides](https://github.com/microsoft/fides) | Formalizes confidentiality/integrity labels, dynamic taint enforcement, selective hiding, and the class of enforceable planner properties. | AgentDojo security/utility taxonomy and task coverage. | Public tutorial notebook, inspected revision `669c046c4adbc56ee49c9672fdd30c54937ea062`; not a complete released benchmark runner. Reconstruct the AgentDojo integration and label it as such. Test label-source trust, declassification, implicit flows, and mislabeled adapters. |
| [Task Shield](https://aclanthology.org/2025.acl-long.1435/) | Evaluates alignment between the user task, intermediate instructions, and tool calls at test time. | BU/utility and ASR on AgentDojo; reported GPT-4o ASR 2.07% with utility 69.79%. | Model-mediated baseline. Evaluate repeated trials and adaptive attacks because its judgment is probabilistic and is not an authorization proof. |
| [AgentSpec](https://github.com/haoyuwang99/AgentSpec) | A small rule DSL with triggers, predicates, and multiple enforcement responses; evaluates code, embodied, and autonomous-driving domains. | Unsafe-call prevention, compliance, rule-generation precision/recall, and millisecond overhead. | Public research code. Port a minimal rule set to the common calendar and workflow cases. Test parser/rule omissions, predicate faults, alternate tool paths, and LLM-generated-rule recall. |
| [Agent-C](https://arxiv.org/abs/2512.23738) | Specifies temporal requirements, translates them to logic, checks during generation, and evaluates both adversarial and benign tasks. | Conformance, harm, utility, and runtime across retail and airline workloads and multiple models. | GitHub currently contains a placeholder, but the open [Zenodo artifact](https://doi.org/10.5281/zenodo.21095899) is complete. Verified archive checksum `md5:e37f84c00035d7d254170e474e938424`; it includes retail, airline, and telecom benign/adversarial splits and AgentSpec/DynaGuard baselines. Test correct ordering with wrong principal/resource, stale authorization, concurrency, and effects outside the temporal alphabet. |
| [ToolGate](https://aclanthology.org/2026.findings-acl.470/) | Makes trusted symbolic state explicit and applies Hoare-style preconditions and verified postconditions before committing state. | Logical validity, state correctness, task success, and overhead on multi-step reasoning. | No public implementation link was found in the arXiv or ACL record during this audit. Implement only a minimal paper-faithful contract baseline and label it clean-room. Test lying tools, valid responses with absent/wrong effects, concurrent interference, and observer compromise. |
| [ToolSafe](https://aclanthology.org/2026.findings-acl.1850/) | Focuses on step-level hazards within multi-step traces and supplies feedback rather than only an end-of-run label. | Unsafe-call detection, task performance, and guardrail classification metrics. | Learned-guard baseline. Its classification output must not be treated as an observed effect or deterministic authorization decision. |
| [TraceSafe](https://arxiv.org/abs/2604.07223) | Tests guardrails at intermediate trajectory positions across security and operational failure categories. | Precision/recall and related classification measures over more than 1,000 trajectories and 12 risk categories. | Use as an offline judgment benchmark and source of trajectory mutations. It does not replace end-to-end execution oracles. |
| [AttriGuard](https://arxiv.org/abs/2603.10749) | Uses counterfactual shadow replay to ask whether a tool call is caused by trusted intent or untrusted observation; evaluates adaptive attacks. | Static/adaptive ASR, utility loss, and runtime overhead across models and benchmarks. | Strong causal-attribution baseline. Test stochastic disagreement, nondeterministic tools, multi-cause actions, delayed triggers, and attacks that preserve action identity but substitute attributes. |
| [BrowseSafe](https://arxiv.org/abs/2511.20597) | Uses realistic HTML payloads and emphasizes real-world browser actions rather than text-only compromise. | Detection/attack outcomes, benign utility, and layered-defense comparisons across frontier models. | Public model weights are available, but complete environment reproduction needs confirmation. Use it as a content detector inside—not instead of—the resource boundary. Test redirects, cross-origin state, downloads, and non-text active content. |
| [PCAS](https://arxiv.org/abs/2602.16708) | Compiles declarative policies into an instrumented reference monitor over agent dependencies. | Policy compliance, utility, and enforcement overhead. | Reproduce if its full artifact is located; otherwise implement only declared policy cases. Test compiler bugs, incomplete dependency graphs, bypass paths, environment effects, and policy/effect disagreement. |

The screen is living literature, but the confirmatory baseline set must be
frozen before running the main study. New papers may be added to related work
without silently changing hypotheses or the test partition.

## Reproduction order

### Stage A: validate the benchmarks

1. Pin AgentDojo and reproduce one published no-defense and one built-in-defense
   condition on a small stratified subset.
2. Run the same cases repeatedly to estimate sampling variance and scorer
   nondeterminism.
3. Reproduce the original and corrected scoring variants described by *Are
   Firewalls All You Need?*.
4. Audit every task for whether the injected content destroys information
   required for benign completion, forces a tool into the plan, or permits a
   brute-force sequence to game the scorer.

Do not begin with a new SENTINEL dataset. First establish that the harness can
recover known results and known benchmark flaws.

### Stage B: reproduce representative defenses

Use one representative from each enforcement family:

- probabilistic content defense: Sanitizer and Task Shield;
- plan/data separation: CaMeL;
- information-flow control: Fides reconstruction;
- per-action rule enforcement: AgentSpec;
- temporal enforcement: Agent-C;
- pre/postcondition enforcement: ToolGate clean-room subset;
- causal action attribution: AttriGuard, if an official artifact becomes
  available.

Every baseline receives the same agent model, temperature, tool schemas,
attempt budget, user tasks, attacker knowledge, and effect oracle when the
system permits it. Native paper metrics are retained in a separate namespace;
they are never silently replaced by SENTINEL metrics.

### Stage C: recreate promptware safely

Reconstruct the *Invitation* scenarios using a synthetic calendar/mail/home
environment. Use fake identities, canary secrets, RFC-reserved domains, and
mock physical devices. Recreate the causal chain, not the proprietary Gemini
implementation:

1. attacker creates an invitation;
2. benign user requests a daily/weekly summary or meeting preparation;
3. hostile fields enter the agent context;
4. the payload attempts an immediate or delayed action;
5. independent sinks record every attempted and completed effect.

Report scenario coverage and behavioral correspondence to the paper. Do not
claim reproduction of a patched, closed service.

## The common fort

The experimental fort is a replaceable defense boundary, not a single model:

```text
authenticated request
        |
trusted task-envelope builder
        |
probabilistic planner -- proposes only --> typed action/workflow
        |
trusted attribute binder
        |
reference monitor + temporal/workflow scheduler
        |
credentialless protocol adapters
        |
narrow credential/effect brokers
        |
real or simulated services
        |
independent effect observers
```

For URLs and files, the fort adds a non-transitive resource state machine:

```text
reference -> fetch -> quarantine -> inspect -> normalize -> render -> execute
```

Each edge is a separate operation. Authority for one edge never implies the
next. Redirects, changed content digests, new origins, decompression, active
rendering, credential use, or execution cause a new policy decision.

The LLM proposal contains only capability name, typed arguments, and declared
data dependencies. The boundary derives principal, tenant, delegation, task,
resource identity, destination, provenance, contract digest, policy version,
current state, credentials, and execution compartment from trusted sources.

## Datasets

Use a federation rather than inventing one monolithic dataset:

| Dataset | Role |
|---|---|
| AgentDojo | Primary comparable tool-agent benchmark and shared CaMeL/Fides/Task Shield substrate. |
| InjecAgent | Breadth across user/attacker tool combinations and staged exfiltration. |
| Agent-C's pinned tau2 artifact | Temporal constraints, long workflows, benign/adversarial customer-service tasks. |
| MUZZLE + The Zoo | Stateful browser execution, adaptive injection surfaces, and actual application-state effects. |
| SENTINEL Calendar/Resource Extension | Stored invitations, delayed triggers, redirects, downloads, archives, parsing, rendering, and cross-service workflows absent from the preceding suites. |

The SENTINEL extension should include benign hard negatives: security training
events, incident-response meetings, code snippets discussing prompt injection,
legitimate links and archives, multilingual invitations, and workflows that
genuinely require a new recipient or destination after trusted user input.
Without these, an always-deny system will appear secure.

Malware-like fixtures must be inert and isolated. Use test signatures,
network/file canaries, MIME mismatches, bounded archive-bomb fixtures, path
traversal names, symlinks, active HTML that targets a local sink, and deliberately
crashing test parsers. Do not use live malware, real secrets, production
accounts, or uncontrolled external callbacks.

## Attack portfolio

Run attacks in four increasing tiers:

1. **Published static attacks:** native AgentDojo, InjecAgent, ASB, and
   reconstructed Invitation payloads.
2. **Compositional attacks:** encoding, multilingual and hidden content,
   tool-return injection, delayed triggers, memory poisoning, redirects, and
   cross-application chains.
3. **Adaptive attacks:** AutoDojo/MUZZLE-style mutation with a fixed query and
   attempt budget, including denial-feedback-aware attacks.
4. **Boundary fault attacks:** provenance dropped, principal/resource swapped,
   policy stale, fail-open timeout, action mutated after authorization, direct
   endpoint bypass, duplicate/reordered delivery, lying success response,
   observer omission, and sandbox/network misconfiguration.

The first three attack the agent. The fourth attacks the trusted computing base.
SENTINEL's strongest differentiator is evaluating both without conflating them.

## Common metrics

Report native metrics plus these effect-grounded measures:

- benign utility (BU) and utility under attack (UA);
- attempted and completed unauthorized-effect rates;
- consequence-weighted compromise rate, reported by consequence rather than as
  an unexplained scalar;
- false-denial rate and always-deny-normalized utility;
- authority amplification: executed authority minus trusted task authority;
- destination/resource substitution rate;
- delayed and cross-session compromise rate;
- missing, duplicate, reordered, stale, and uncompensated effects;
- verdict/receipt/environment disagreement rate;
- containment failure at fetch, quarantine, inspect, render, and execute;
- minimal assurance cut-set size under boundary faults;
- latency, tokens, model calls, policy time, and sandbox cold-start cost.

Use paired trials on identical initial state. Report per-task results and
bootstrap confidence intervals, not only pooled percentages. Use multiple
sampling seeds for probabilistic components. A defense is not credited for a
safe refusal without the refusal also reducing its utility score.

## Pre-registered research questions

- **RQ1:** Can the study recover published trends and known benchmark defects
  for AgentDojo and its defenses?
- **RQ2:** Which enforcement family best preserves useful completion under
  static and adaptive promptware?
- **RQ3:** Can untrusted content change an authoritative attribute while the
  nominal tool and action type remain allowed?
- **RQ4:** Do preconditions, temporal constraints, or information-flow labels
  remain sound when adapters, catalogs, policy inputs, brokers, and observers
  are faulty?
- **RQ5:** Does a non-transitive resource state machine contain malicious URL
  and file handling without collapsing benign meeting-preparation utility?
- **RQ6:** Which smallest combinations of agent manipulation and boundary fault
  produce an unauthorized real effect?

## Decision gate for the paper

SENTINEL should not be presented as a new deterministic boundary if CaMeL,
Fides, Agent-C, ToolGate, or PCAS already covers the tested property. The paper
proceeds only if experiments support at least one narrower claim:

1. trusted attribute binding prevents attacks that preserve a locally valid
   tool call while substituting identity, resource, destination, delegation, or
   provenance;
2. non-transitive resource transitions contain browser/file attacks that
   action-only guards do not model;
3. effect-grounded observation detects false success, bypass, duplication, or
   compensation failures missed by symbolic state alone; or
4. cross-layer fault injection exposes minimal assurance cut sets not measured
   by agent-only benchmarks.

If none is supported, the scientifically correct output is a replication and
negative-result paper rather than a novelty claim.
