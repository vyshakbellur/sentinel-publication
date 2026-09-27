# SENTINEL publication plan: DSN 2027

## Target

Primary target: IEEE/IFIP DSN 2027 regular research track. Planned abstract
deadline: 2026-11-25; planned paper deadline: 2026-12-02. Maintain an anonymous
submission branch and artifact bundle. Post the fuller preprint to arXiv only
after the experimental claims and figures freeze; use a title distinct from the
blind submission and do not advertise concurrent review.

Working title: **SENTINEL: Effect-Grounded Conformance Testing of Deterministic
Boundaries for Agentic Microservice Workflows**

## Central thesis

A probabilistic agent may propose a typed workflow, but a deterministic boundary
must own authority, dependency/conflict semantics, scheduling, actuation,
response validation, and the definition of success. A correct local policy
decision is insufficient evidence of a safe workflow. Assurance must cover the
whole proposal-to-effect chain and use independently observed effects,
including combinations of faults inside the boundary itself.

## Research questions

- RQ1: Which single and interacting cross-layer faults yield unauthorized,
  missing, duplicated, or misreported effects?
- RQ2: How much does trusted binding reduce unsafe effects relative to no
  guard, schema/allowlist validation, and policy-only enforcement?
- RQ3: Do guardrail-local decisions agree with independently observed effects?
- RQ4: What safety–recovery–latency trade-off does each mechanism occupy?
- RQ5: Which failures and minimal cut sets transfer across realistic systems?
- RQ6: Do equivalent operations preserve canonical action, authorization, and
  effects across protocol representations and adapters?
- RQ7: Do allowed parallel schedules preserve the safety and terminal state of
  their serial equivalents under delay, retry, replay, and partial failure?

## Contributions required for acceptance

1. A protocol-neutral canonical workflow/effect model that separates untrusted
   agent proposals from trusted identity, authority, resource, dependency,
   conflict, contract, and state facts.
2. An effect-grounded conformance oracle covering protocol equivalence,
   complete mediation, dependency authenticity, schedule invariance, decision
   correctness, observed effects, recovery, and observation fidelity.
3. A cross-layer fault model and automated cut-set minimizer for failures in
   contracts, adapters, binding, graph validation, scheduling, authorization,
   delivery, compensation, and observation.
4. A controlled comparison on two maintained public microservice systems,
   supplemented by a protocol-adapter conformance suite.
5. A reusable artifact containing locked dependencies, frozen proposals and
   workflows, replay tools, analysis, and curated counterexamples.

## Experimental systems

- Primary: Google Online Boutique and OpenTelemetry Astronomy Shop.
- Fault injection: Chaos Mesh plus SENTINEL's control-plane fault adapters.
- Replication: Train Ticket; DeathStarBench only as a stretch goal.
- Predictor inputs: ARIA-generated proposals frozen before guardrail comparison.
- Guardrails: no guard, JSON schema + allowlist, OPA or Cedar policy-only,
  Guardian trusted binding + policy, and an always-deny sanity baseline.

Protocol scope: use OpenAPI/HTTP and gRPC on the realistic systems first. Add
GraphQL, SOAP/WSDL, and AsyncAPI as adapter-conformance subjects unless a
maintained public system supports a credible end-to-end effect experiment.
Breadth of parser fixtures must not be presented as breadth of deployment
evidence.

Use the same proposed action, starting state, load trace, and injected faults
for every guardrail. Each actuator must carry a unique experiment and action ID
so duplicate and substituted execution can be detected independently.

## Factorial design

Layers: input/provenance, predictor, protocol contract/adapter, binding,
dependency/conflict graph, policy, scheduler/retry state, broker/delivery,
environment effect, response/observation, and compensation/recording. Start
with all single faults and all pairwise cross-layer faults;
promote only failure-preserving pairs into higher-order search. Include benign
perturbations and hard negatives to measure availability and false blocking.

Use three disjoint phases. Run the complete 58-row covering design once per
system/guardrail cell as a descriptive fault-surface census. Estimate
infrastructure variance in a blinded 12-row pilot. Then power and repeat the
preregistered 19-row confirmatory subset across independent deployment,
incident-template, and load-seed blocks. Retain all terminal outcomes and
predeclare exclusions. Do not treat repeated calls against one unchanged
deployment as independent observations or use an arbitrary repetition count.

## Metrics and analysis

- Unsafe-effect rate and severity-weighted unsafe-effect rate.
- Recovery success, time to recovery, and service-level objective impact.
- False block/escalation rate on legitimate actions.
- Decision/effect and observation/effect disagreement rates.
- Duplicate, missing, substituted, and out-of-scope effects.
- Guardrail latency, end-to-end latency, and resource overhead.
- Minimal cut-set size, composition, frequency, and cross-system transfer.

Report Wilson or exact binomial intervals for rates; bootstrap intervals for
latency and recovery; paired tests or hierarchical models for matched trials;
effect sizes and multiplicity correction. Publish raw counts alongside all
normalized metrics. Never report “zero risk”; report the upper confidence bound.

## Ablations

- Remove trusted attribute binding.
- Trust predictor-supplied scope or destination.
- Remove independent effect observation.
- Disable idempotency/action IDs.
- Replace fail-closed handling with permissive fallback.
- Vary catalog freshness and provenance authentication.
- Compare exhaustive pairs with guided cut-set search.

## Paper structure

1. Motivation and failure example.
2. System and threat model.
3. SENTINEL methodology and terminal-record contract.
4. Implementation and guardrail adapters.
5. Experimental design and reproducibility controls.
6. Results organized by the five RQs.
7. Industry comparison and related work.
8. Limitations, threats to validity, and responsible-use statement.

## Evidence gates

- **G0 — complete now:** simulator contracts, effect oracle, fault plumbing,
  immutable records, first minimal cut sets, bundled Guardian tests.
- **G1 — Oct 5:** executable Online Boutique adapter; no-guard, allowlist, and
  Guardian baselines; one-click local cluster protocol.
- **G2 — Oct 19:** OTel Demo adapter, Chaos Mesh faults, independent Kubernetes
  effect observer, and pilot variance estimates.
- **G3 — Nov 2:** full single/pairwise runs, minimization, statistical notebook,
  and frozen RQs/hypotheses.
- **G4 — Nov 16:** replication or explicit scope decision, ablations, figures,
  limitations, and artifact dry run on a clean machine.
- **G5 — Nov 25:** anonymous abstract and complete internal draft.
- **G6 — Dec 2:** DSN submission and versioned private artifact snapshot.

## Immediate implementation order

1. Define Kubernetes actuator and effect-observer interfaces without coupling
   them to one workload.
2. Build Online Boutique service/deployment discovery and scale/restart actions.
3. Add baseline adapters and frozen-proposal import.
4. Add Chaos Mesh experiment generation and state restoration checks.
5. Run pilots before expanding the factorial matrix.
6. Implement OTel Demo by mapping the same abstract actions, not by forking the
   harness.

If G2 slips by more than one week, submit a focused DSN practical-experience or
tool paper only if the evidence genuinely supports it; otherwise preserve the
regular-paper study for ISSRE rather than weakening the claims.
