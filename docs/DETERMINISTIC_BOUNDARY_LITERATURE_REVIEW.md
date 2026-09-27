# Deterministic boundaries for probabilistic agents: literature and gap review

Last updated: 2026-09-27

## Review question

What is already known about placing a deterministic boundary around a
probabilistic agent, and what can SENTINEL contribute beyond existing agent
guardrails, workflow engines, policy systems, and API contracts?

This review uses primary papers, standards, and official product documentation.
Preprints are labeled as such. Product documentation is evidence of deployed
capability, not evidence of research novelty or effectiveness.

## Answer in one paragraph

The architectural principle is correct but is no longer novel by itself.
Simplex and runtime shielding established external safety authority before the
LLM era. CaMeL and Fides separate trusted control from untrusted data. AgentSpec,
Agent-C, FORGE, ToolGate, ActGov, and out-of-band policy enforcement place
deterministic checks around agent actions, histories, or state transitions.
Temporal, BPMN, Step Functions, and Serverless Workflow already implement
dependency-aware sequential and parallel execution. OpenAPI, WSDL/SOAP,
GraphQL, gRPC, and AsyncAPI already describe heterogeneous service contracts.
SENTINEL should therefore not claim invention of the deterministic boundary,
contracts, or workflow DAGs. Its strongest defensible contribution is an
**effect-grounded conformance and fault-assurance layer**: normalize multiple
protocols into one action/effect graph, test complete mediation and workflow
semantics under cross-layer faults, and judge the result using independent
environment effects rather than the boundary's own verdict or tool response.

## Literature map

### 1. External deterministic safety authority

| Work | Established result | Consequence for SENTINEL |
|---|---|---|
| [Simplex](https://doi.org/10.1109/REAL.1998.739773) (1998) | An unverified advanced controller can be separated from a trusted decision mechanism and safe fallback. | Do not claim the trusted boundary pattern as new. |
| [Safe reinforcement learning via shielding](https://doi.org/10.1609/aaai.v32i1.11797) (AAAI 2018) | A formal shield can prevent unsafe actions from reaching an environment. | Do not claim action interception or shielding as new. |
| [Runtime-assurance verification framework](https://ntrs.nasa.gov/citations/20240006807) (NASA, 2024) | Runtime assurance is only as sound as its monitor, model, switching logic, and assumptions. | Supports treating the assurance chain itself as a test target. |
| [Trustworthy Agentic AI Requires Deterministic Architectural Boundaries](https://arxiv.org/abs/2602.09947) (preprint, 2026) | Explicitly argues for finite action calculus, reference monitoring, information-flow labels, and privilege separation around agents. | The phrase “deterministic boundary around a probabilistic agent” is directly occupied prior art. |

### 2. Agent-specific enforcement

| Work | Enforcement object | What remains outside its central evaluation |
|---|---|---|
| [CaMeL](https://arxiv.org/abs/2503.18813) (preprint, 2025) | Trusted control/data-flow separation and capabilities prevent untrusted tool data from changing program flow. | Cross-layer faults in catalogs, adapters, execution, and outcome observation. |
| [Fides](https://arxiv.org/abs/2505.23643) (preprint, 2025) | A planner tracks confidentiality/integrity labels and deterministically enforces information-flow policy. | Real-effect fault coverage of the complete actuation chain. |
| [AgentSpec](https://arxiv.org/abs/2503.18666) (preprint, 2025) | A DSL expresses triggers, predicates, and runtime enforcement rules. | Protocol-equivalence and independently observed workflow effects. |
| [Agent-C](https://arxiv.org/abs/2512.23738) (preprint, 2025) | Temporal constraints enforce ordering properties such as authentication before access. | Faults in the boundary itself and post-action effect fidelity. |
| [FORGE / Formal Policy Enforcement for Real-World Agentic Systems](https://arxiv.org/abs/2602.16708) (preprint, 2026) | Datalog policies use causal execution context and a reference monitor; an observability service has an assume/guarantee contract. | Empirical violation of those assumptions across protocol, broker, observer, and environment layers. |
| [ToolGate](https://aclanthology.org/2026.findings-acl.470/) (Findings of ACL 2026) | Hoare-style preconditions and postconditions gate tool execution and symbolic-state updates. | Independent environment-state oracles, concurrent workflow conflicts, and fault coverage. |
| [ActGov](https://arxiv.org/abs/2609.24446) (preprint, 2026) | Each tool action is abstracted into a policy record and checked against task-scoped authorization in dynamic workflows. | Protocol-normalization equivalence and effect-grounded failures of enforcement assumptions. |
| [Out-of-Band Policy Enforcement](https://arxiv.org/abs/2608.27646) (preprint, 2026) | A trusted proxy authorizes typed operations/resources and filters requests and responses outside agent reasoning. | The paper explicitly leaves write controls, durable approval, and temporal/aggregate policies outside its evaluation. |
| [Deterministic ToolGuards for company policy](https://aclanthology.org/2025.emnlp-industry.41/) (EMNLP Industry 2025) | Natural-language policies are compiled offline into code that guards each tool call. | End-to-end boundary fault injection and real effect/recovery oracles. |

These systems make three claims unavailable to SENTINEL: deterministic
pre-action checking is new; pre/post action contracts are new; or temporal and
causal policy over a workflow is new.

### 3. Workflow semantics are mature prior art

| System or standard | Existing capability | Boundary not supplied by it |
|---|---|---|
| [BPMN 2.0](https://www.omg.org/spec/BPMN/2.0/PDF) | Sequence flows, parallel splits, synchronization, choices, events, and compensation-oriented process modeling. | Agent-specific trust binding and effect authorization. |
| [Workflow Patterns](https://pure.tue.nl/ws/files/2053121/613310.pdf) | A catalog of control-flow patterns including sequence, parallel split, synchronization, and interleaving. | Security policy or independent effect assurance. |
| [Sagas](https://doi.org/10.1145/38713.38742) | Long-lived transactions decomposed into steps with compensating actions. | Whether an untrusted agent was authorized to select the saga or its arguments. |
| [Temporal](https://docs.temporal.io/) | Durable workflows, deterministic replay, activity retry/timeout policy, histories, and compensation patterns. | Semantic authorization of the agent's proposed operation and independently observed safety. |
| [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) | State machines, choice, parallel and map execution, timeouts, retries, and execution history. | A general trusted binder or effect oracle for agent-proposed actions. |
| [CNCF Serverless Workflow](https://serverlessworkflow.io/) | A portable workflow DSL with calls, forks, events, retries, and multiple protocol integrations. | Complete mediation and adversarial fault assurance for an agent boundary. |

Parallel scheduling is therefore an engineering requirement, not the novelty.
SENTINEL can add a security property over it: only nodes proven independent in
data, authority, resource, and effect domains may run concurrently, and the
equivalence between allowed serializations and the parallel execution must be
tested from actual effects.

### 4. API contracts and protocol surfaces

| Surface | Authoritative contract | Relevant semantics | SENTINEL adapter obligation |
|---|---|---|---|
| REST/HTTP | [OpenAPI 3.2](https://spec.openapis.org/oas/latest.html) | Operations, parameters, bodies, responses, schemas, security schemes, callbacks, and links. | Bind `operationId`/operation reference, server, method, path, media type, request and response schemas. |
| SOAP | [SOAP 1.2](https://www.w3.org/TR/soap12-part1/) + [WSDL](https://www.w3.org/TR/wsdl20/) + [WS-Security](https://www.oasis-open.org/standards#wssv1.1.1) | XML envelopes, service operations, message types, bindings, signatures, timestamps, and faults. | Canonicalize XML, bind QName/operation/endpoint, verify signatures and freshness, validate output or fault contract. |
| GraphQL | [GraphQL specification](https://spec.graphql.org/September2025/) | Typed query/mutation/subscription validation and execution; mutation fields have serial execution semantics. | Bind persisted operation and variables, cap query cost/depth, distinguish query from effectful mutation, validate response shape and errors. |
| gRPC | [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) + Protocol Buffers descriptors | Unary and streaming RPCs generated from typed service definitions. | Bind service/method, descriptor digest, metadata identity, deadlines, cardinality, and status/trailer contract. |
| Event-driven APIs | [AsyncAPI 3.1](https://github.com/asyncapi/spec/blob/master/spec/asyncapi.md) | Protocol-neutral channels, operations, messages, security schemes, and bindings. | Bind channel/action/message schema, correlation and partition identity, delivery semantics, and acknowledgement/effect observation. |
| Agent tools | MCP, A2A, and framework function schemas | Tool discovery and invocation envelopes. | Treat descriptions and returned content as untrusted data; resolve to a separately trusted capability manifest. |

Interface schemas establish syntactic compatibility. They normally do not say
whether a particular principal may cause an effect now, whether two apparently
independent calls conflict, whether a retry duplicated the effect, or whether a
successful response corresponds to the intended environment state. Those are
the boundary semantics SENTINEL must model and test.

### 5. Deployed policy and gateway controls

| Control | What exists in industry | Gap relevant to SENTINEL |
|---|---|---|
| [Open Policy Agent](https://www.openpolicyagent.org/docs) | Domain-neutral policy decisions over structured data in microservices, Kubernetes, CI/CD, and gateways. | OPA intentionally separates decision from enforcement; a correct decision does not prove the intended effect. |
| [Cedar](https://docs.cedarpolicy.com/) | Deterministic principal-action-resource-context authorization with analyzable policies. | The application still constructs facts and performs the authorized operation. |
| [Istio AuthorizationPolicy](https://istio.io/latest/docs/reference/config/security/authorization-policy/) | Workload-level request mediation and external authorization in service meshes. | Does not validate a multi-step agent goal, output dataflow, compensation, or application-level recovery. |
| [Kong AI Gateway](https://developer.konghq.com/ai-gateway/) | Authentication, traffic governance, prompt/response filters, MCP/A2A routing, OAuth-scoped tools, and observability. | Gateway controls do not by themselves establish causal workflow correctness or real-effect safety. |
| [Temporal](https://docs.temporal.io/) and Step Functions | Production-grade durable orchestration and histories. | Reliability guarantees are not authorization or safety guarantees. |
| [OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | Industry guidance already recommends minimum functionality, permissions, autonomy, and independent approval of high-impact actions. | Guidance needs an executable, measurable assurance method. |
| [NIST SP 800-207A](https://csrc.nist.gov/pubs/sp/800/207/a/final) | Zero-trust guidance applies identity- and application-aware policy enforcement to cloud-native microservices. | It does not evaluate agent workflow semantics or effect-oracle disagreement. |

### 6. Evaluation work

AgentDojo and related prompt-injection benchmarks measure whether an attacker
causes a forbidden agent behavior while the agent attempts a user task.
Trace-level guardrail benchmarks assess judgments along trajectories. NIST's
agent-hijacking work emphasizes adaptive attacks, repeated attempts, and
consequence-specific metrics. Fault-localization work such as AGENTCHAOSBENCH
asks whether a model can identify failures from telemetry.

SENTINEL's distinct dependent variables should be:

1. the effects that actually occurred, including missing, duplicate,
   substituted, out-of-order, and out-of-scope effects;
2. recovery and compensation after partial workflow completion;
3. disagreement among policy verdict, transport response, broker receipt,
   observer report, and independently sampled environment state;
4. the smallest cross-layer fault set that breaks the boundary; and
5. safety, useful completion, recovery latency, and enforcement overhead
   together rather than a safety score alone.

## The publishable gap

### Central architectural thesis

An LLM may propose **what** goal or typed workflow might satisfy a request. It
must not determine **whether**, **with whose authority**, **against which exact
resource**, **in what causally valid order**, or **whether the resulting effect
counts as success**. Those decisions belong to a deterministic boundary using
trusted state and independent observation.

### Narrow novelty claim

SENTINEL is a protocol-neutral, effect-grounded method for testing the fault
coverage of deterministic agent workflow boundaries. It checks whether the
same logical intent is bound, authorized, scheduled, executed, and observed
consistently across heterogeneous service protocols and under faults spanning
input provenance, contract adapters, dependency graphs, policy facts,
enforcement, delivery, compensation, and observation.

This is intentionally narrower than claiming a new reference monitor, policy
language, workflow engine, API description, or formal proof of safety.

## Novel assurance relations to test

The following relations are plausible original contributions when implemented
and empirically evaluated:

1. **Protocol-representation invariance.** Equivalent REST, SOAP, GraphQL,
   gRPC, or asynchronous representations of the same registered capability
   must produce the same canonical action, authority scope, and policy verdict.
2. **Schedule invariance for independent nodes.** Permuting or parallelizing
   nodes declared independent must not change authorized effects or terminal
   state beyond declared commutative fields.
3. **Conflict serialization.** Nodes sharing a non-commutative effect domain
   must never overlap, even if the agent labels them independent.
4. **Dependency authenticity.** A node may consume only schema-valid,
   provenance-bound fields from completed predecessors; tool text never becomes
   control flow or authority.
5. **Commit-time freshness.** Authorization is rechecked against trusted current
   state immediately before an irreversible effect, not only when the plan was
   proposed.
6. **Response/effect agreement.** A syntactically valid success response cannot
   satisfy a postcondition unless an independent observer confirms the declared
   effect within a bounded window.
7. **Retry/compensation conservation.** Retry, replay, timeout, crash, and
   compensation faults must yield an allowed terminal effect multiset, not just
   a successful workflow status.
8. **Complete mediation.** Every effect-capable route and protocol must produce
   a boundary receipt; bypasses, shadow endpoints, and alternate protocols are
   explicit test failures.

## What would falsify the novelty claim

The paper must weaken or abandon the claim if a prior system is found that
jointly provides all of the following and evaluates them empirically:

- heterogeneous protocol normalization into a common effect-aware workflow IR;
- trusted binding of identity, resource, authority, and provenance;
- deterministic dependency/conflict scheduling with commit-time authorization;
- independently observed postconditions and compensation outcomes; and
- cross-layer fault injection with minimal assurance cut sets and
  safety--recovery--latency analysis.

Finding a system with one or several elements is expected and should be cited
as a baseline, not hidden.

## Review limitations

This is a structured gap review, not yet a systematic literature review under
PRISMA. Before submission, record databases, exact queries, screening dates,
deduplication, inclusion/exclusion reasons, publication status, and forward and
backward citation chasing. Preprints published after the experimental design is
frozen should be added to related work and, where feasible, to baselines without
retroactively changing confirmatory hypotheses.
