# Iteration 16: baseline-fidelity and novelty-falsification milestone

Timestamp: 2026-09-29T00:35:06Z

## Research question

After executing or reconstructing CaMeL, Agent-C, Fides, and ToolGate, which
SENTINEL claims remain empirically distinguishable from prior art, which broad
claims must be eliminated, and is the current evidence sufficient for a
publication-ready result?

## Competing explanations

- H1: the deterministic boundary, typed action contracts, provenance tracking,
  temporal enforcement, or pre/postcondition state verification remains a novel
  SENTINEL mechanism.
- H2: complete trusted action-tuple construction remains a narrow empirical gap
  across more than one enforcement family while preserving at least one valid
  baseline action under the SENTINEL control.
- H3: independent effect observation does not change conclusions beyond native
  scorers or symbolic-state verdicts.
- H4: non-transitive resource transitions and assurance cut sets already have
  executed evidence and can be claimed as results.
- H5: enough matched, held-out, repeated evidence exists to call the paper
  publication-ready.

## Smallest discriminating action

Freeze a machine-readable decision audit before execution. Hash-bind the
accepted AgentDojo, CaMeL, SENTINEL tuple, Agent-C, Fides, and ToolGate reports;
extract their comparable mechanism facts; apply explicit elimination and
retention thresholds; and fail if any evidence file has changed. Eliminate a
mechanism novelty claim when one direct prior-art family implements it. Retain
an empirical candidate only when multiple distinct contexts meet the frozen
threshold and a positive utility control exists where required.

## Acceptance and falsification criteria

- All eight source reports must match their recorded SHA-256 digests.
- All five broad mechanism claims must be eliminated when their declared direct
  prior art is present.
- Trusted attribute binding is retained only if at least two baseline families
  show the selected gap and the SENTINEL tuple control preserves its baseline
  while blocking every preregistered mutation.
- Effect observation is retained only if at least two distinct contexts contain
  a native-verdict/effect disagreement.
- A candidate with no executed evidence must remain an untested hypothesis.
- Publication readiness requires all five frozen evidence gates: matched
  end-to-end trials, held-out confirmation, repeated probabilistic seeds,
  uncertainty intervals, and realistic multi-service effects.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/milestone16_claim_audit.json`, SHA-256
  `8f68eaac602740bf3b7aaff72a289b54659810f6652af59f7f3921de54f9cb3a`.
- Audit runner: `scripts/audit_milestone16_claims.py`, SHA-256
  `e086398ab800d491284d6e620384abd252ba98a2ffc0d80b1fb89a5092f14070`.
- Accepted raw report:
  `_workloads/reproduction/iteration-16-claim-audit-v1/report.json`, SHA-256
  `4a7a5cedd1cacc031dd778f90b73d3cecc9667018aa278782daaff729abe5443`.
- Input report digests are embedded in both the protocol and accepted report:
  AgentDojo iteration 4; CaMeL static and dynamic iteration 8; SENTINEL tuple
  iteration 11; Agent-C iteration 12; Fides tutorial and reconstruction
  iterations 13–14; ToolGate iteration 15.
- Host/interpreter: Darwin arm64, CPython 3.12.7. This audit performs no model,
  network, service, or external action.

## Results

All evidence hashes verified and the audit met its frozen acceptance rule.

### Claims eliminated as novel mechanisms

| Claim | Direct prior-art families | Milestone decision |
|---|---|---|
| Deterministic boundary | CaMeL, Fides, Agent-C, ToolGate | eliminate |
| Information flow and provenance | CaMeL, Fides | eliminate |
| Temporal workflow enforcement | Agent-C | eliminate |
| Preconditions, postconditions, symbolic state | ToolGate | eliminate |
| Typed action contracts | ToolGate, Agent-C | eliminate |

These mechanisms may remain components or baselines, but none can be presented
as SENTINEL inventions.

### Narrow candidates retained

Trusted attribute binding met its retention threshold across three distinct
baseline families:

- CaMeL: only 2/10 audited side-effect operations strictly bind their complete
  authority-bearing tuples, and three untrusted resource selectors produced
  observed effects;
- Agent-C: 1/19 released write policies formally binds the complete
  confirmation tuple, and all three domain-stratified same-identity value
  substitutions were admitted while identity substitutions were denied; and
- ToolGate: an existence-only precondition admitted and executed the selected
  substituted destination.

The paired SENTINEL tuple control retained baseline utility and blocked 7/7
mutations. This supports a narrow candidate about **trusted construction and
complete binding of normalized action attributes**. It does not support novelty
for equality predicates or action contracts, which the baselines can express.

Independent effect observation also met its retention threshold in two
different contexts. AgentDojo had one declared native scorer/effect disagreement
in 64 frozen pairs. ToolGate had two native symbolic-commit/effect disagreements
in seven deliberately faulted cases. This supports a cross-layer disagreement
evaluation contribution, not novelty for application-state assertions.

### Claims not yet supported

Non-transitive URL/file resource transitions remain an **untested hypothesis**.
Fides adapter mislabeling and ToolGate executor/result faults motivate
cross-layer assurance cut sets, but no combined-fault or minimal-cut-set
experiment has run. That claim is therefore **motivated but untested**.

Baseline fidelity remains heterogeneous, and zero published effectiveness
numbers have been reproduced:

- CaMeL: artifact execution and deterministic policy probes;
- Agent-C: artifact replication with dependency substitutions and model-free
  replay;
- Fides: tutorial artifact execution plus a conceptual AgentDojo
  reconstruction; and
- ToolGate: official artifact mechanism execution.

All five publication-readiness gates are missing. The audit therefore returns
`publication_ready: false`.

## Deviations

No new defense execution was needed because the milestone question concerns the
logical consistency and scope of already accepted evidence. Unlike a
documentation-only restatement, the audit was frozen first, cryptographically
bound to eight raw reports, extracted the decision variables, and applied
falsifiable thresholds. A changed report, missing positive control, single
evidence context, or fulfilled publication gate would change or fail the result.

The protocol's direct-prior-art map is based on the previously verified
literature ledger rather than a new systematic database search in this
iteration.

The first reference-integrity command omitted the repository from
`PYTHONPATH` and failed at import before validation. The corrected command
`PYTHONPATH=. python scripts/check_references.py` verified all 31 entries; the
failed invocation did not touch evidence or change the audit.

## Limitations

The evidence is development-only and heterogeneous. CaMeL, Agent-C, and
ToolGate gaps are tested under different tasks and notions of authorization;
they do not yet form a matched effect-size comparison. The Fides comparison is
a conceptual reconstruction. The single SENTINEL positive result covers one
Agent-C address rule and seven mutations.

The audit verifies hashes and declared extraction rules, not the semantic
correctness of every earlier manual field classification or literature mapping.
Thresholds of two contexts or families are decision rules for continuing the
study, not statistical evidence of generality. There are no confidence
intervals, repeated stochastic trials, held-out results, realistic provenance-
producing attacks, or multi-service workflow effects.

Independent effect checking is established prior art in benchmarks and
stateful application testing. Only its use to expose cross-layer
verdict/receipt/effect disagreement remains a candidate study contribution.

## Interpretation

H1, H3, H4, and H5 are rejected. H2 is supported only as a narrow development
hypothesis. The original theme—placing determinism around a probabilistic
agent—is important architecture but occupied prior art. SENTINEL should no
longer be framed as a new guardrail or policy language.

The scientifically strongest direction is a cross-layer assurance evaluation:
construct authoritative action tuples from trusted inputs, preserve each
baseline's native enforcement semantics, inject faults into both the agent and
the trusted boundary, and compare native decisions with independently observed
effects. Guardian is the reference implementation used to instantiate and
ablate this methodology, not the sole source of novelty.

## Publication impact

The milestone forces a narrower and more credible paper. The leading positive
path is an empirical assurance/evaluation paper with two linked results:

1. locally valid enforcement can still consume incompletely authenticated
   action attributes; and
2. native verdict or symbolic-state success can disagree with external effects
   under boundary faults.

The negative-results path is also viable: a reproducibility and assurance-gap
study showing that strong deterministic defenses address different properties,
their public artifacts have heterogeneous reproducibility, and native metrics
do not jointly establish end-to-end authority and effect fidelity.

Neither path is ready for arXiv. The paper still needs a common trace/effect
interface, broader independent oracles, matched substitutions, realistic
calendar/resource scenarios, held-out adaptive confirmation, and uncertainty
analysis.

## Minimum interface requirements for iteration 17

The common record must preserve each baseline's native metric namespace and add
without reinterpretation: proposal identity and raw arguments; normalized
operation and arguments; trusted principal, tenant, resource, destination,
provenance, delegation, contract, policy, and freshness bindings; native
decision and reason; dispatch identity; returned response/receipt; independently
observed effect tuple; pre/post state digests; injected faults; and explicit
decision/dispatch/receipt/effect disagreement flags.

## Decision

**Continue with a narrowed framing.** Iteration 17 should implement and validate
the common append-only action/effect trace schema against the already accepted
CaMeL, Agent-C, Fides, and ToolGate evidence without changing their native
scores. Do not begin URL/file or cut-set claims until the shared evidence model
can distinguish decisions, dispatches, receipts, and effects.
