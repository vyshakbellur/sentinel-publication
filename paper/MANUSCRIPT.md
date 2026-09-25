# SENTINEL: Cross-Layer Fault Injection for Evaluating Deterministic Guardrails in Predictive Remediation Systems

**Manuscript status:** pre-results research draft; not publication-ready  
**Target:** arXiv preprint after completion of the registered experiments; then ARR or a systems/dependability journal according to the final emphasis  
**Warning:** do not upload this version. Bracketed fields require measured evidence.

## Abstract

Predictive systems increasingly propose or initiate consequential actions, including recovery operations in cloud services. Deterministic runtime guardrails are intended to prevent a fallible or compromised predictor from causing unauthorized effects. Existing work provides policy languages, reference monitors, information-flow controls, signed authorization, freshness checks, and guarded remediation controllers. Their guarantees, however, depend on a chain of assumptions about evidence, trusted attributes, policy state, enforcement, and outcome observation. Nominal policy-conformance tests do not measure how failures in those assumptions propagate into protected-system effects. We introduce **SENTINEL**, a cross-layer fault-injection methodology for evaluating deterministic guardrails around predictive remediation systems. SENTINEL perturbs six stages of the prediction-to-effect pipeline: operational evidence, prediction, trusted binding, policy decision, execution enforcement, and outcome observation. It measures unauthorized effects, safe recovery, false intervention, rollback success, and recovery latency using environment-state oracles. We instantiate the methodology using ARIA as a fallible microservice-diagnosis and remediation proposer, Guardian as a deterministic reference guardrail, and public microservice systems as execution environments. Across **[N]** incident-action trials and **[F]** fault configurations, cross-layer faults **[PRIMARY RESULT]**. Compared with **[BASELINE]**, Guardian **[RESULT]**, while **[ABLATION]** exposes **[FAILURE MODE]**. These results show **[EVIDENCE-SUPPORTED CONCLUSION]** and establish a reproducible method for testing guardrails as safety-critical software rather than assuming their correctness from nominal behavior.

## 1. Introduction

Machine-learning and large-language-model components increasingly sit upstream of consequential software actions. In cloud operations, a model may interpret telemetry, localize a failure, choose a remediation, and invoke an infrastructure API. The model can be wrong because of ordinary prediction error, distribution shift, incomplete evidence, poisoned telemetry, or malicious instructions. A common response is to place a deterministic policy or reference monitor between the model and the environment.

This architectural pattern is well established. Runtime-assurance and shielding systems place an unverified advanced component behind a trusted safety mechanism. Agent-security systems such as CaMeL, Fides, AgentSpec, PCAS, and AgentFlow enforce capabilities, information-flow constraints, or declarative policies outside the model. Other systems bind authority to actions, histories, or execution evidence. In cloud operations, AIOpsLab, MicroRemed, R2Act, and ARBITER move evaluation from diagnosis toward executable remediation.

External enforcement is necessary, but it does not make the surrounding system infallible. A deterministic decision can be consistently wrong when its resource catalog is stale. A correctly authorized action can be substituted or replayed at execution. A fail-closed dependency can prevent harm while also preventing recovery. An action can return success without restoring the service. A postcondition monitor can observe delayed or corrupted signals. These are faults in the assurance chain rather than failures of the language model alone.

Existing evaluations commonly measure attack success, policy classification, task completion, recovery-plan validity, or fault diagnosis. These measures answer important but different questions. A policy-conformance score does not reveal whether an unauthorized effect reached the environment. Endpoint success does not reveal whether recovery was authorized. Fault-label accuracy does not reveal whether a guardrail contained the fault. As a result, we lack a systematic way to measure the **fault coverage** of deterministic guardrails around predictive systems.

We present SENTINEL, a cross-layer fault-injection methodology for this purpose. SENTINEL models the complete path from operational evidence to observed recovery. It injects controlled faults into the evidence, predictor, trusted binder, policy, enforcement point, and outcome observer, both individually and in selected combinations. Each trial is graded by independently defined state and safety oracles.

We instantiate SENTINEL in microservice remediation. ARIA produces diagnoses and typed remediation proposals from public benchmark evidence. Its outputs, including confidence and suggested risk, are treated as untrusted. Guardian independently binds identity, capability, resource, destination, tenant, manifest, policy, and current state before deciding whether an action may execute. A broker is the only component with mutation credentials. Public microservice environments determine whether the authorized effect occurred and whether service health recovered.

This work makes four intended contributions:

1. **A cross-layer fault model** for deterministic guardrails around predictive action systems, spanning evidence through outcome observation and defining metamorphic assurance relations that should remain invariant under untrusted-input transformations.
2. **A reproducible fault-injection harness** that evaluates actual effects and recovery rather than guardrail verdicts alone.
3. **An empirical study** of nominal, single-fault, and pairwise cross-layer behavior across multiple public microservice systems and guardrail configurations, including minimization of unsafe traces into assurance cut sets.
4. **An assurance-recovery analysis** that quantifies unauthorized effects, safe recovery, false intervention, rollback, and latency as a joint frontier.

The contribution is an evaluation method and empirical result. We do not claim to invent external enforcement, risk-adaptive authorization, action contracts, commit-time freshness, replay protection, causal provenance, or guarded Kubernetes remediation.

## 2. Background and Related Work

### 2.1 Runtime assurance and shielding

The Simplex architecture separates an unverified advanced controller from a trusted decision mechanism and a safety-preserving fallback. Runtime shielding similarly prevents a learning agent from executing actions that violate a formal specification. These systems establish two principles relevant here: safety authority must remain outside the learning component, and any guarantee is relative to the fidelity of the safety specification and environment model.
[@seto1998simplex; @alshiekh2018shielding; @slagel2024rta]

SENTINEL starts from these principles and evaluates their operational assumptions. Rather than synthesizing a new shield, it perturbs the inputs and components on which a software guardrail depends and observes whether protected-system safety and recovery are preserved.

### 2.2 Runtime enforcement for LLM agents

CaMeL separates trusted control flow from untrusted data and uses capabilities to prevent unauthorized exfiltration. Fides formalizes information-flow control for agent planners. AgentSpec supplies a runtime-constraint language, while Agent-C enforces temporal constraints. PCAS compiles policies into an instrumented reference monitor over dependency graphs. AgentFlow adds flow-centric policies and bounded formal verification.
[@debenedetti2025camel; @costa2025fides; @wang2025agentspec; @palumbo2026pcas]

ToolGate uses Hoare-style preconditions and verified postconditions to protect a
symbolic state during tool execution [@liu2026toolgate]. It is especially close
contract-level prior art. SENTINEL's proposed novelty is not action contracts;
it is the cross-layer, effect-grounded fault evaluation of the wider assurance
chain in which such contracts operate.

These systems establish the breadth of deterministic runtime enforcement. SENTINEL does not propose a competing policy language. It evaluates how such enforcement behaves when trusted attributes, policy data, dependencies, or enforcement paths are faulty.

### 2.3 Authority, provenance, and durable effects

Open Agent Passport studies per-action authorization and signed audit records. Commit-time authorization requires earlier authority evidence to remain fresh, causally prior, effect-bound, and eligible when a durable effect occurs. CapLease shows that single-use identifiers do not prevent semantic replay without durable authorization state. Causal-reference-monitor work models information learned from denied actions. Proof-of-execution work binds a contract, causal history, effect, and replay context into a verifiable execution artifact.

These mechanisms can strengthen a Guardian implementation, but they are prior art rather than our novelty. SENTINEL uses substitution, staleness, replay, denial feedback, and incomplete history as fault operators and measures the residual consequences under different defenses.

### 2.4 Guardrail benchmarks

AgentDojo evaluates indirect prompt injection in tool-using agents. Task Shield evaluates task alignment. TraceSafe-Bench evaluates mid-trajectory guardrail judgment. NIST has shown that adaptive attacks, consequence-specific reporting, and repeated attempts can materially change apparent agent robustness.
[@debenedetti2024agentdojo; @jia2025taskshield; @chen2026tracesafe; @mou2026toolsafe; @nist2025hijacking]

AGENTCHAOSBENCH is the closest methodological neighbor: it injects operational faults at model, tool, guardrail, and inter-agent boundaries and asks models to detect and localize those faults from telemetry. SENTINEL asks a different question. It evaluates whether the assurance architecture prevents prohibited effects and preserves recovery after a fault is injected. Its primary labels are environment safety and recovery outcomes, not fault type or location.

Metamorphic testing addresses systems for which complete expected-output oracles are difficult to construct by checking relations between source and transformed executions. It has been applied to LLM behavior and autonomous systems. SENTINEL does not claim this testing method as new; it defines assurance-specific relations over authority, freshness, identity, risk, and effects and combines them with cross-layer fault injection and independent environment-state oracles.

### 2.5 Autonomous remediation

AIOpsLab evaluates agents over cloud incident lifecycles, while MicroRemed evaluates executable remediation generation. R2Act shows that high diagnostic accuracy does not imply valid recovery actions. ARBITER implements typed, policy-gated Kubernetes remediation. Risk-constrained remediation work combines blast radius, reversibility, epistemic uncertainty, and adaptive human review. AIOpsDoom shows that manipulated telemetry can steer AIOps agents toward harmful actions.
[@chen2025aiopslab]

These studies motivate our domain and baselines. SENTINEL's distinction is to test the fault coverage of the protection chain itself, including interactions among evidence faults, predictor errors, authority faults, enforcement faults, and outcome-observation faults.

## 3. System Model

### 3.1 Prediction-to-effect pipeline

We model one remediation trial as:

\[
e \xrightarrow{P} d,a_p \xrightarrow{B} a_c \xrightarrow{D} v,o
\xrightarrow{X} s' \xrightarrow{O} r,
\]

where:

- \(e\) is operational evidence;
- \(P\) is a fallible predictor producing diagnosis \(d\) and proposed action \(a_p\);
- \(B\) binds the proposal to trusted context, producing canonical action \(a_c\);
- \(D\) is the policy decision function producing verdict \(v\) and obligations \(o\);
- \(X\) is the enforcement/execution mechanism;
- \(s'\) is the resulting environment state; and
- \(O\) observes recovery and produces outcome record \(r\).

An action may be blocked, escalated, transformed into a bounded fallback, executed, or compensated after a failed postcondition.

### 3.2 Safety and recovery oracles

For incident \(i\), initial state \(s_i\), and effect trace \(\tau_i\), an independent policy oracle defines:

\[
Safe(i, \tau_i) \in \{0,1\}.
\]

An independent environment oracle defines:

\[
Recovered(i, s'_i, W) \in \{0,1\},
\]

where \(W\) is a predeclared observation window. The agent, predictor, and guardrail may not define either oracle after observing results.

**Safe recovery** occurs only when both predicates equal one. An endpoint that appears healthy after an unauthorized mutation is an unsafe success, not a safe recovery.

### 3.3 Trusted computing base

The declared trusted computing base includes:

- experiment controller and fault scheduler;
- ground-truth incident and action manifests;
- oracle definitions;
- root keys or test signing keys;
- broker credential isolation;
- terminal record writer.

Guardian, ARIA, policy bundles, catalogs, state caches, providers, and observers can each be faulted according to the experiment condition. The paper's guarantees apply only when the stated trusted-computing-base assumptions hold.

## 4. SENTINEL Fault Model

### 4.1 Evidence faults

- stale telemetry window;
- missing modality;
- value manipulation within schema;
- service-label alias corruption;
- faithful versus shuffled or reversed topology;
- poisoned log or trace content.

### 4.2 Predictor faults

- wrong root-cause service;
- wrong fault type;
- inadmissible action for a correct diagnosis;
- excessive action magnitude;
- malformed arguments;
- overconfident incorrect proposal.

Natural ARIA errors are preserved. Controlled mutations supplement them without being counted as independent model errors.

### 4.3 Binding faults

- stale capability manifest;
- incorrect resource or destination mapping;
- cross-tenant alias collision;
- missing provenance object;
- agent-asserted security attribute accepted as authoritative;
- policy/manifest version mismatch ignored.

### 4.4 Policy faults

- omitted deny or escalation rule;
- conflicting permit and deny rules;
- stale policy bundle;
- provider timeout;
- fail-open default;
- incorrectly lowered risk tier;
- cached approval after revocation.

Policy mutations should be systematic and schema-valid. Each mutant records the exact operator and expected semantic change.

### 4.5 Enforcement faults

- guardrail bypass;
- argument substitution after decision;
- stale state at commit time;
- duplicate execution through retry or concurrency;
- partial external effect before crash;
- unauthorized fresh reissuance;
- broker/result mismatch.

### 4.6 Observation faults

- success response with no state change;
- delayed health regression outside a short observation window;
- corrupted outcome receipt;
- missing rollback confirmation;
- monitoring blind spot;
- stale postcondition evidence.

## 5. Research Questions and Hypotheses

**RQ1: Fault coverage.** Which single-layer faults produce unauthorized effects under each guardrail configuration?

**RQ2: Cross-layer interaction.** Which fault pairs produce non-additive increases in unauthorized effects or recovery failures?

**RQ3: Safety-utility tradeoff.** How do stronger fail-closed and full-verification configurations affect safe recovery, false intervention, and time to recovery?

**RQ4: Adaptive verification.** Under which fault classes does risk-adaptive verification remain equivalent to full verification, and when does it lose safety?

**RQ5: Outcome fidelity.** How often do authorization or tool-return metrics disagree with independently observed recovery and safety?

**RQ6: Assurance structure.** Which minimal fault combinations and metamorphic-relation violations characterize the actual containment boundary of each guardrail configuration?

Pre-registered hypotheses:

- **H1:** faults in trusted binding or enforcement cause a higher unauthorized-effect rate than predictor-only faults because they invalidate the containment boundary;
- **H2:** pairwise faults spanning a trusted-input layer and enforcement layer exhibit positive interaction beyond their single-fault risk differences;
- **H3:** fail-closed enforcement reduces unauthorized effects but increases false intervention and recovery time;
- **H4:** a mandatory deterministic verification floor prevents adaptive routing from increasing unauthorized effects under predictor-confidence faults;
- **H5:** environment postcondition oracles identify false recovery outcomes missed by authorization-decision and tool-return metrics;
- **H6:** cross-layer minimization produces recurring assurance cut sets that transfer across incidents and at least two system environments.

## 6. Experimental Design

### 6.1 Systems and incidents

Use at least two public microservice systems; three are preferred:

- Online Boutique;
- Train Ticket;
- OpenTelemetry Astronomy Shop.

Incident evidence should come from canonical public benchmark readers or a declared live fault-injection testbed. Do not infer ground truth from directory names. Freeze incident IDs, repository revisions, container images, deployment manifests, and oracle definitions before the confirmatory run.

### 6.2 Predictor conditions

- deterministic ARIA RCA/remediation;
- at least two LLM configurations from different model families;
- oracle proposal control;
- deliberately incorrect proposal control.

For stochastic predictors, use predeclared seeds and repeated trials. Predictor outputs must be frozen before guardrail-condition comparison so every guardrail sees identical proposals.

### 6.3 Guardrail conditions

1. **No external guardrail:** direct execution within the simulator/testbed.
2. **Schema and allowlist only:** typed action plus static capability exposure.
3. **Guardian static:** trusted binding plus deterministic per-action policy.
4. **Guardian full:** all configured contextual checks, freshness, durable consumption, and postconditions.
5. **Guardian adaptive:** mandatory deterministic floor with risk-selected deeper checks or approval.
6. **External policy baseline:** equivalent rules expressed in OPA/Rego or Cedar where feasible.

The external-policy condition tests whether results arise from Sentinel's methodology or Guardian-specific implementation choices.

### 6.4 Fault campaign

Run:

- nominal controls;
- every single fault operator;
- within-layer representative pairs;
- cross-layer pairs chosen through a preregistered pairwise covering array;
- a small set of hand-designed high-risk compound scenarios.

For every unsafe compound trace, apply fault-set minimization: remove one operator at a time and rerun the frozen trial until no proper subset reproduces the effect. Record the remaining minimal assurance cut set. Separately run preregistered metamorphic transformations, including lower predictor confidence, greater declared blast radius, older evidence, changed agent-asserted tenant, canonical resource alias substitution, and duplicate effect identifiers. Each relation must state the expected verdict/effect ordering before execution.

Do not run an unconstrained full factorial. It will be expensive and difficult to interpret. Pairwise combinatorial testing provides systematic interaction coverage while preserving feasibility.

### 6.5 Primary outcomes

**Unauthorized Effect Rate (UER)**

\[
UER = \frac{\sum_i \mathbb{1}[Effect_i \land \neg Safe_i]}{N}.
\]

**Safe Recovery Rate (SRR)**

\[
SRR = \frac{\sum_i \mathbb{1}[Recovered_i \land Safe_i]}{N}.
\]

**False Intervention Rate (FIR)** is the fraction of oracle-safe proposals that are blocked or unnecessarily escalated.

**Containment Coverage (CC)** is the proportion of faulted unsafe proposals that do not create an unauthorized external effect.

**Assurance cut-set size** is the cardinality of the smallest injected fault set that reproducibly causes a defined unauthorized effect for a frozen trial.

Secondary outcomes include unsafe success, failed-safe outcomes, rollback success, duplicate-effect rate, metamorphic-relation violation rate, postcondition disagreement, human escalation rate, deep-verifier invocation rate, and p50/p95/p99 decision and recovery latency.

### 6.6 Statistical analysis

- Use paired comparisons because identical frozen proposals run under each guardrail condition.
- Report absolute risk differences, relative risks where denominators permit, and confidence intervals.
- Model binary outcomes with mixed-effects logistic regression or cluster-aware generalized estimating equations, clustering at incident and system levels.
- Estimate fault-pair interaction on an additive risk scale and report model-based interaction coefficients as sensitivity analysis.
- Use cluster bootstrap intervals for recovery latency and rate differences.
- Apply Holm correction to the preregistered primary comparisons.
- Report raw discordant counts and all terminal failures.
- Never convert zero observed events into a zero population rate; report an exact or appropriate cluster-aware upper bound.

Power and final sample size must be chosen after a blinded infrastructure pilot that estimates event rates and variance without testing the primary hypotheses.

## 7. Reproducibility and Artifact Design

Every run should emit one immutable terminal record containing:

- incident and environment revision;
- predictor name, model digest, prompt/context digests, and generation settings;
- untrusted proposal;
- trusted canonical action;
- policy and manifest digests;
- injected fault operators and seeds;
- decision, obligations, and reasons;
- broker request and effect identifiers;
- pre-state and post-state digests;
- recovery and safety oracle outputs;
- latency components;
- rollback/compensation outcome;
- code revision and dependency lock digest.

Paper tables and figures must be generated exclusively from these records. The artifact checker must fail if a reported number does not reproduce from the frozen run set.

## 8. Results

### 8.1 Nominal behavior

Report nominal UER, SRR, FIR, escalation, rollback, and latency for every condition. Nominal correctness is necessary but not the primary contribution.

| Condition | UER | SRR | FIR | Escalation | p95 decision latency | p95 recovery time |
|---|---:|---:|---:|---:|---:|---:|
| No guardrail | [ ] | [ ] | [ ] | - | [ ] | [ ] |
| Schema/allowlist | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Guardian static | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Guardian full | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Guardian adaptive | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| External policy | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### 8.2 Single-fault coverage

Report outcomes by fault operator and layer. Avoid an aggregate “accuracy” that hides high-consequence failures.

### 8.3 Cross-layer interactions

Present a layer-by-layer interaction heatmap using absolute UER increase over the nominal condition. Identify which pairs exceed the additive expectation and verify them with targeted reruns.

### 8.4 Safety-recovery frontier

Plot SRR against UER, with latency or escalation encoded separately. A strong result moves toward high safe recovery and low unauthorized effects; pure refusal should not appear superior merely because it prevents execution.

### 8.5 Assurance cut sets and metamorphic relations

Report the distribution and recurrence of minimized assurance cut sets by architecture, system, and unsafe-effect class. Separate portable cut sets from implementation-specific ones. For each preregistered metamorphic relation, report violation counts and minimized counterexamples.

### 8.6 Outcome disagreement

Compare:

- policy decision;
- tool-return success;
- observed effect;
- safety oracle;
- recovery oracle.

Quantify how often earlier-stage metrics overstate safe recovery.

## 9. Discussion

The discussion must be driven by results. Candidate questions include:

- Which assumptions form the real containment boundary?
- Are predictor errors contained while trusted-data errors pass through?
- Does progressive verification retain its cost advantage under realistic fault rates?
- Which faults require architectural controls rather than better model prompts?
- How much recovery utility is lost through fail-closed behavior?
- Which observations transfer across systems and which are topology-specific?

The paper should distinguish three forms of assurance:

1. **policy correctness:** the rule expresses the intended restriction;
2. **decision correctness:** the engine evaluates the supplied facts correctly;
3. **effect correctness:** only the authorized effect occurs and the observed outcome is genuine.

SENTINEL primarily evaluates the gaps between these layers.

## 10. Threats to Validity

**Construct validity.** Safety policies and recovery oracles simplify operational judgment. Each must be reviewed independently and versioned before experiments.

**Internal validity.** Fault injection can introduce unrealistic artifacts. Operators should preserve schemas and plausible timing, and clean/faulted trials should share identical base incidents.

**External validity.** Public microservice systems do not represent every production environment. Claims should be limited to the evaluated action vocabulary, policies, and fault model.

**Statistical validity.** Incident repetitions and fault variants are not independent samples. Analysis must cluster by incident and system and distinguish natural model errors from controlled mutations.

**Implementation validity.** Guardian is both a research prototype and a system under test. Equivalent external-policy baselines, ablations, and fault-oracle tests reduce author-implementation bias.

## 11. Limitations

SENTINEL cannot establish that a policy is complete or morally correct. Deterministic enforcement only guarantees behavior relative to the facts, state model, policies, credentials, and enforcement coverage supplied to it. Fault operators approximate possible failures and cannot enumerate all adversarial strategies. A simulator improves reproducibility but may omit Kubernetes races, controller interactions, or delayed effects. A live testbed improves realism but adds environmental variance. Results from microservice remediation may not transfer to finance, healthcare, robotics, or open-ended computer-use agents without new action and safety models. The study evaluates bounded actions and does not solve general prompt injection, compromised tool implementations, or malicious infrastructure administrators.

## 12. Ethical Considerations

Experiments should use public datasets, synthetic secrets, reserved destinations, and isolated test environments. No production credentials or externally reachable destructive tools should be available to an agent. Telemetry attacks and enforcement bypasses should be disclosed only as reproducible test fixtures against disposable systems. The paper should avoid describing finite-sample containment as universal security.

## 13. Conclusion

Deterministic guardrails are increasingly proposed as the safety boundary around predictive and agentic systems. Their presence alone does not establish dependable behavior. SENTINEL treats the guardrail and its assumptions as testable safety-critical software. By injecting faults across evidence, prediction, binding, policy, enforcement, and observation, and grading actual effects and recovery, the methodology is designed to reveal assurance failures hidden by nominal conformance and endpoint-success metrics. **[Insert result-grounded conclusion after confirmatory experiments.]**

## References to include in the formatted manuscript

Seventeen core references below have publisher/proceedings/government/arXiv
metadata recorded in `references/core_references.json` and matching entries in
`paper/references.bib`. Entries without a BibTeX key remain candidates and must
not support final novelty claims until verified.

1. Alshiekh et al. [Safe Reinforcement Learning via Shielding](https://ojs.aaai.org/index.php/AAAI/article/view/11797). AAAI, 2018. `alshiekh2018shielding`.
2. Angelopoulos et al. [Conformal Risk Control](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html). ICLR, 2024. `angelopoulos2024crc`.
3. Debenedetti et al. [AgentDojo](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html). NeurIPS Datasets and Benchmarks, 2024. `debenedetti2024agentdojo`.
4. Debenedetti et al. [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813). 2025.
5. Costa et al. [Securing AI Agents with Information-Flow Control](https://arxiv.org/abs/2505.23643). 2025.
6. Wang et al. [AgentSpec](https://arxiv.org/abs/2503.18666). 2025/2026.
7. Jia et al. [The Task Shield](https://aclanthology.org/2025.acl-long.1435/). ACL, 2025.
8. Palumbo et al. [Policy Compiler for Secure Agentic Systems](https://arxiv.org/abs/2602.16708). 2026.
9. Uchibeke. [Before the Tool Call](https://arxiv.org/abs/2603.20953). 2026.
10. Chinaei. [Causality Laundering](https://arxiv.org/abs/2604.04035). 2026.
11. Santos-Grueiro. [Temporary Authority, Permanent Effects](https://arxiv.org/abs/2607.10487). 2026.
12. Xu et al. [Beyond Single-Use Tokens](https://arxiv.org/abs/2608.01710). 2026.
13. Rhodes and Kang. [Proof of Execution](https://arxiv.org/abs/2607.05397). 2026.
14. Shivakumar et al. [AgentFlow](https://arxiv.org/abs/2608.22868). 2026.
15. Zhang et al. [When Agentic Executions Fail](https://arxiv.org/abs/2608.14680). 2026.
16. Pasquini et al. [When AIOps Become “AI Oops”](https://arxiv.org/abs/2508.06394). 2025.
17. Zhang et al. [MicroRemed](https://arxiv.org/abs/2511.01166). 2025.
18. Qi et al. [Can LLMs Really Recover Microservice Failures?](https://arxiv.org/abs/2607.04623). 2026.
19. Dai et al. [Safe Remediation as Risk-Constrained Intervention](https://arxiv.org/abs/2607.20005). 2026.
20. Habibi and Leon-Garcia. [ARBITER](https://arxiv.org/abs/2607.19182). 2026.
21. Ponduru et al. [RACER](https://www.multiresearchjournal.com/arclist/list-2026.6.5/id-6834). 2026.
22. NIST. [Strengthening AI Agent Hijacking Evaluations](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations). 2025.
23. Seto et al. [The Simplex Architecture for Safe Online Control System Upgrades](https://doi.org/10.1109/ACC.1998.703255). American Control Conference, 1998. `seto1998simplex`.
24. Geifman and El-Yaniv. [SelectiveNet: A Deep Neural Network with an Integrated Reject Option](https://proceedings.mlr.press/v97/geifman19a.html). ICML, 2019.
25. Kamath et al. [Enforcing Temporal Constraints for LLM Agents](https://arxiv.org/abs/2512.23738). 2025.
26. Chen et al. [TraceSafe: A Systematic Assessment of LLM Guardrails on Multi-Step Tool-Calling Trajectories](https://arxiv.org/abs/2604.07223). 2026.
27. Mou et al. [ToolSafe: Enhancing Tool Invocation Safety of LLM-based Agents via Proactive Step-level Guardrail and Feedback](https://aclanthology.org/2026.findings-acl.1850/). Findings of ACL, 2026.
28. Chen et al. [AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds](https://proceedings.mlsys.org/paper_files/paper/2025/file/d1f9e4a9f109b6e8b75ed362736f22ec-Paper-Conference.pdf). MLSys, 2025. `chen2025aiopslab`.
29. Slagel et al. [A Formal Verification Framework for Runtime Assurance](https://ntrs.nasa.gov/citations/20230017350). NASA Formal Methods, 2024. `slagel2024rta`.
30. Cho et al. [LLMORPH: Automated Metamorphic Testing of Large Language Models](https://valerio-terragni.github.io/assets/pdf/cho-ase-2025.pdf). ASE, 2025.
31. Liang et al. [AutoMT: A Multi-Agent LLM Framework for Automated Metamorphic Testing of Autonomous Driving Systems](https://arxiv.org/abs/2510.19438). 2025.
32. Liu et al. [ToolGate: Contract-Grounded and Verified Tool Execution for LLMs](https://aclanthology.org/2026.findings-acl.470/). Findings of ACL, 2026. `liu2026toolgate`.

## Publication-readiness gate

Before arXiv upload, all boxes must be satisfied:

- [ ] primary hypotheses and comparisons preregistered;
- [ ] fault operators reviewed and frozen;
- [ ] at least two system environments validated;
- [ ] safety and recovery oracles tested independently;
- [ ] baseline implementations complete;
- [ ] blinded pilot completed and sample size fixed;
- [ ] confirmatory experiment completed without post-outcome exclusions;
- [ ] tables and figures regenerated from immutable terminal records;
- [ ] all zero-event claims include uncertainty bounds;
- [ ] limitations and ethical considerations finalized;
- [ ] repository/data artifact sanitized and archived;
- [ ] references verified against final versions and DOIs;
- [ ] author contributions and model-assistance disclosures completed;
- [ ] manuscript converted to the selected venue template;
- [ ] no bracketed placeholders remain.
