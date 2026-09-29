# Iteration 20 milestone: prior-art subtraction and claim audit

Timestamp: 2026-09-29T01:39:15Z

## Research question

After subtracting capabilities already established by CaMeL, Agent-C, Fides,
ToolGate, policy systems, and standard message-integrity mechanisms, which
SENTINEL claim is still supported strongly enough to justify the remaining
calendar, resource-transition, adaptive-attack, and cut-set experiments?

## Competing explanations

- H1: iteration 19 establishes a novel deterministic guardrail.
- H2: complete tuple predicates, digest sealing, or application-state checks
  are individually novel mechanisms.
- H3: the evidence supports only a replication/negative-results paper.
- H4: a narrower effect-grounded, cross-layer assurance-evaluation claim
  survives, with trusted complete-tuple construction as a reference mechanism.
- H5: the paper is already ready for arXiv because deterministic synthetic
  coverage reached 100% in the selected matrix.

## Smallest discriminating action

Freeze a hash-bound audit over the milestone-16 prior-art report and the
accepted iteration-17 common trace, iteration-18 effect-oracle matrix, and
iteration-19 tuple-substitution matrix. Apply preregistered retention rules,
separate enabling mechanisms from candidate contributions, and evaluate seven
publication-readiness gates independently of synthetic pass rates.

## Acceptance and falsification criteria

- Verify all four source-report hashes and inherit all five milestone-16
  mechanism-novelty eliminations.
- Retain trusted complete-tuple construction only if gaps remain across at
  least three baseline families, six authority dimensions are exercised, all
  paired SENTINEL benign controls pass, all substitutions are contained, and
  utility exceeds always-deny.
- Retain effect correspondence only if native/effect disagreement exists in at
  least two prior contexts and at least four controlled effect-failure classes.
- Treat the common trace as a supporting artifact, not a research result.
- Treat the digest seal, equality predicates, and application-state assertions
  as enabling controls rather than novel primitives.
- Publication readiness requires every listed gate; a single missing gate
  falsifies readiness.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/milestone20_claim_audit.json`, SHA-256
  `0aa02f7d8e3deaf435f2f01cd625ae0932db05d05aa7e2e47f56f28275c263b5`.
- Audit implementation: `scripts/audit_milestone20_claims.py`, SHA-256
  `33ef7bba10f875f6b5f79143372a5ba3fd2f5b43e94762fc372893b737a5d009`.
- Accepted raw report:
  `_workloads/reproduction/iteration-20-claim-audit-v1/report.json`, SHA-256
  `d5bc56b8470b56bf018abeca3b0f8a5333ecc26c285e7372f05837220ba6ae7b`.
- Verified input hashes are recorded in both protocol and report: milestone 16
  `4a7a5ced...`, iteration 17 `3bc5e9b2...`, iteration 18 `2acd20cc...`,
  and iteration 19 `e8f63210...`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network, service,
  or external effect was invoked.

## Results

The audit passed and reproduced byte-for-byte from a fresh output path. It
inherited five prior-art eliminations and made the following decisions:

| Candidate | Milestone-20 decision |
|---|---|
| Deterministic boundary | Not novel |
| IFC/provenance enforcement | Not novel |
| Temporal workflow enforcement | Not novel |
| Preconditions/postconditions and symbolic state | Not novel |
| Typed action contracts | Not novel |
| Tuple equality predicates | Enabling mechanism, not novelty |
| Policy-to-execution digest seal | Enabling mechanism, not novelty |
| Application-state assertions | Enabling mechanism, not novelty |
| Common action/effect trace | Supporting artifact only |
| Trusted complete-tuple construction | Retain as mechanism-supported candidate |
| Cross-layer effect correspondence | Retain as primary evaluation candidate |
| Non-transitive resource transitions | Untested hypothesis |
| Minimal assurance cut sets | Motivated but untested |

The retained tuple candidate is grounded in observed gaps across CaMeL,
Agent-C, and ToolGate plus the six-dimension iteration-19 mechanism matrix.
SENTINEL retained 12/12 paired benign controls and contained 24/24 selected
substitutions, whereas always-deny retained 0/12 benign controls.

The retained effect candidate has two prior disagreement contexts—AgentDojo's
native scorer and ToolGate's symbolic commit—and five controlled failure
classes: wrong target, post-decision argument substitution, false success,
duplicate retry, and partial effect. Iteration 18 observed ten claimed
successes without safe recovery.

All seven publication gates remain missing: matched published-baseline trials,
a held-out confirmatory partition, probabilistic repeated seeds, uncertainty
intervals, realistic multi-service effects, an independently authenticated
observer, and adaptive attack evaluation. `publication_ready` is therefore
false.

## Deviations

No deviation from the frozen protocol. The audit used the previously verified
literature/prior-art ledger rather than reopening the search during this
milestone. Its purpose was claim subtraction against accepted evidence, not a
new systematic literature review.

## Limitations

The milestone is a deterministic evidence audit, not a new defense experiment.
Its retention thresholds are study-governance rules, not statistical
confidence. The milestone-16 report transitively binds earlier baseline
reports, but this audit does not independently repeat every semantic
classification.

The tuple evidence is still synthetic and the protocol names do not establish
wire-level REST, SOAP, or GraphQL equivalence. The effect observer is not
externally authenticated. No matched published defense has been run on the
iteration-19 matrix. No stochastic end-to-end attack result or interval exists.
Consequently, neither retained candidate is currently a general efficacy or
novelty theorem.

## Interpretation

H1, H2, and H5 are rejected. H3 remains a viable fallback, but H4 is the
strongest positive direction. Guardian should be presented as a reference
implementation that makes the assurance relations executable. SENTINEL's
primary research object is not the guardrail itself; it is the cross-layer
correspondence among authenticated intent, canonical action, policy verdict,
broker execution, receipt, independent effect, and recovered state under
faults.

The paper should ask three empirical questions:

1. Where do public deterministic defenses leave authority-bearing tuple fields
   incomplete or assume trusted adapters?
2. How often do native verdicts, receipts, and symbolic state disagree with
   independently observed effects under matched faults?
3. What smallest combinations of assurance-layer failures permit unauthorized
   effects while preserving an apparently successful workflow?

The first two have development evidence; the third remains untested.

## Publication impact

The preferred framing is an **effect-grounded cross-layer assurance evaluation
with trusted complete-tuple construction**, with Guardian as the reference
implementation and a replication/negative-results fallback. This is more
credible than a paper claiming a new deterministic boundary.

The remaining iterations have a clear burden of proof. Iterations 21–24 must
demonstrate realistic stored promptware and non-transitive URL/file transitions
with benign hard negatives and matched defense families. Iterations 25–27 must
freeze adaptive attacks, minimize cross-layer cut sets, and run a held-out
confirmatory analysis with uncertainty. Failure at those gates should trigger
the negative-results framing rather than inflate synthetic mechanism coverage.

## Decision

**Continue with narrowed framing.** Iteration 21 should implement the synthetic
calendar promptware environment and benign hard negatives. The experiment must
record actual attempted/completed effects, keep invitations and linked content
as data rather than instructions, and preserve useful meeting-preparation
workflows. It must not use live malware or claim reproduction of a closed
commercial service.
