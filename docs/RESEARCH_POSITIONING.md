# SENTINEL research positioning

## Architectural thesis

A probabilistic agent may propose typed goals and workflows, but a deterministic
boundary must own authority, dependency and conflict semantics, execution,
response validation, and the definition of successful real-world effects.

## One-sentence research claim

SENTINEL is a protocol-neutral, effect-grounded conformance and fault-injection
methodology that tests whether a deterministic agent workflow boundary still
provides complete mediation when proposal, contract adapter, trusted binding,
dependency graph, policy, scheduling, execution, and observation layers fail
alone and in combination.

## What the market already provides

Commercial and open systems already offer deterministic policy decisions,
prompt/output filters, tool-call interception, workload chaos, runbook
automation, and observability. Those are components or operational controls.
They generally do not establish that a guarded predictive remediation chain
produced only authorized real-world effects under interacting assurance faults.

## Defensible differentiation

SENTINEL's contribution is not “deterministic guardrails” by itself. Guardian
is the reference boundary; SENTINEL is the assurance layer. The publishable
difference is the evaluation object, metamorphic relations, and oracle:

1. Faults span input provenance, prediction, protocol normalization, trusted
   binding, workflow dependencies, policy, scheduling, enforcement, and
   post-action observation—not just the application or model.
2. Success is judged from independently observed system effects and recovery,
   not from the guardrail's own allow/deny return value.
3. Minimal assurance cut sets expose the smallest interacting failures that
   permit an unsafe effect. Cut-set analysis is established; its use as an
   empirical guardrail-assurance output is the contribution.
4. Frozen proposals permit differential evaluation of Guardian, Cedar/OPA, and
   simpler allowlist/schema baselines without model nondeterminism.
5. The analysis reports a safety–recovery–latency frontier, preventing an
   always-deny mechanism from winning on safety alone.
6. Every failure produces a replayable terminal record and minimized
   counterexample suitable for regression and incident analysis.
7. Equivalent operations expressed through REST, SOAP, GraphQL, gRPC, or
   asynchronous APIs can be checked for canonical-action and verdict
   invariance instead of assuming adapters preserve security semantics.
8. Parallel schedules are tested against serial equivalents and effect-conflict
   rules, exposing races, stale authorization, replay, and false independence.

## Claims we must not make yet

- Formal proof of end-to-end safety.
- Generalization beyond the tested systems and fault model.
- Novelty of fault injection, metamorphic testing, policy-as-code, or minimal
  cut sets in isolation.
- Novelty of action contracts, workflow DAGs, parallel scheduling, sagas,
  protocol schemas, temporal policy, or deterministic tool-call interception.
- Production readiness based on the deterministic simulator.

The strongest claim is an empirical systems result: component-level controls
can appear correct under their own outputs while cross-layer, protocol-aware,
effect-grounded testing reveals unsafe workflow effects, ordering violations,
and observation disagreement.

See `DETERMINISTIC_BOUNDARY_LITERATURE_REVIEW.md` for the primary-source gap
review and `WORKFLOW_BOUNDARY_ARCHITECTURE.md` for the proposed system model.
