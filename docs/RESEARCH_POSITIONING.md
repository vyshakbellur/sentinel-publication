# SENTINEL research positioning

## One-sentence claim

SENTINEL is an effect-grounded, cross-layer fault-injection methodology that
tests whether deterministic guardrails still constrain predictive remediation
when the predictor, trusted binding, policy, enforcement, and observation
layers fail alone and in combination.

## What the market already provides

Commercial and open systems already offer deterministic policy decisions,
prompt/output filters, tool-call interception, workload chaos, runbook
automation, and observability. Those are components or operational controls.
They generally do not establish that a guarded predictive remediation chain
produced only authorized real-world effects under interacting assurance faults.

## Defensible differentiation

SENTINEL's contribution is not “deterministic guardrails” by itself. Its
publishable difference is the evaluation object and oracle:

1. Faults span evidence, prediction, trusted binding, policy, enforcement, and
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

## Claims we must not make yet

- Formal proof of end-to-end safety.
- Generalization beyond the tested systems and fault model.
- Novelty of fault injection, metamorphic testing, policy-as-code, or minimal
  cut sets in isolation.
- Production readiness based on the deterministic simulator.

The strongest claim is an empirical systems result: existing component-level
controls can appear correct under their own outputs while cross-layer,
effect-grounded testing reveals unsafe effects and observation disagreement.
