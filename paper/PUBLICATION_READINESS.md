# SENTINEL publication-readiness ledger

Last reviewed: 2026-09-24

Iteration budget: **5/25 completed**. Stop after Cycle 25, or earlier if every
publication gate passes. The final cycle must record a readiness verdict and
all remaining blockers before pausing the publication automation.

## Current verdict

**Not publishable as a research paper.** The novelty claim and experimental
protocol are credible, but the evidence supports only a simulator/harness
demonstration. The abstract, results, and conclusion still contain placeholders.

Current maturity: **protocol + E0 harness validation**.

## Release gates

| Gate | Status | Evidence or blocker |
|---|---|---|
| Defensible novelty statement | Pass | Effect-grounded cross-layer guardrail evaluation; does not claim deterministic enforcement itself as new. |
| Complete manuscript without placeholders | Fail | Abstract, results tables, discussion, and conclusion await confirmatory results. |
| References verified against primary sources | Fail | Candidate bibliography exists; venue/version/DOI verification is incomplete. |
| Independent oracle fixtures | Pass | Eleven deterministic fixtures cover safe/no-effect, wrong target, duplicate identity and semantic effects, excessive and partial effects, false success, rollback, delayed regression, and stale observation. Live calibration remains separate. |
| Frozen threat model and fault catalog | Pass | Versioned machine-readable v1 catalog declares all 11 implemented operators; five primary contrasts, exclusions, non-exclusions, pairing, and analysis rules are frozen before live-pilot outcomes. |
| Meaningful baselines | Partial | No-guard and schema/allowlist simulator paths now run beside Guardian on frozen proposals; OPA/Cedar and live-system baselines remain. |
| First realistic public system | Fail | Online Boutique is revision-locked but not deployed or actuated by SENTINEL. |
| Second realistic public system | Fail | OTel Demo is revision-locked but not deployed or actuated by SENTINEL. |
| Repeated trials and uncertainty | Fail | Current evidence is nine deterministic smoke trials; no confirmatory sampling or intervals. |
| Cross-layer interaction analysis | Partial | A deterministic 58-row design covers nominal, all 11 singles, and all 46 exact cross-layer operator pairs; execution and live-system confirmation remain. |
| Ablations | Fail | Planned but not executed. |
| Clean-environment artifact reproduction | Fail | Unit suite passes locally; no clean-machine/container reproduction report. |
| Anonymous venue package | Fail | Markdown draft only; no DSN template, anonymized artifact, or generated figures. |

## Critical reviewer findings

### P0 — Claims exceed evidence

The draft proposes a multi-system empirical study but currently contains no
realistic-system results. The nine-trial simulator result must be labeled E0 and
must never populate the confirmatory result tables.

### P0 — Missing comparisons

The schema/allowlist baseline is implemented for simulator studies, but no
external policy engine is integrated. Without OPA or Cedar on the same frozen
proposals, reviewers cannot fully separate the methodology's value from
Guardian-specific behavior.

### P0 — No statistical experiment

There are no repeated stochastic/live trials, uncertainty estimates, blocked
randomization, pilot variance estimates, or frozen sample size.

### P0 — Live-system runtime unavailable

The current host has no reachable Docker daemon and no `kubectl`, Kind,
Minikube, or Helm client. Repository and simulator work can continue, but
Online Boutique and OTel Demo trials cannot run until a disposable Kubernetes
environment is installed or attached.

### P1 — Live oracle calibration is incomplete

The effect oracle is a separate function that receives neither policy verdict
nor tool-return success, and its current semantic contract is fixture-tested.
Recovery windows and signal freshness still require calibration against both
live systems before confirmatory use.

### P1 — Manuscript/reference integrity

The bibliography is a candidate list rather than a verified `.bib` database.
Several recent works need primary-source verification and correct publication
status before they can support novelty claims.

## Review–fix–run–analyze history

### Cycle 1 — 2026-09-24

- **Review:** classified the manuscript as a pre-results protocol draft; found
  all confirmatory publication gates unmet.
- **Fix:** copied the manuscript into the research repository; extracted the
  inline effect oracle into an independent module; added seven known-outcome
  oracle fixtures, including semantic duplicate detection with distinct IDs.
- **Run:** 129 unit/regression tests passed; the SENTINEL source/test linter
  passed. Replaying the nine-trial smoke campaign reproduced four synthetic
  unauthorized effects, one observation disagreement, and the same five
  minimized findings.
- **Analyze:** the existing nine-trial smoke result demonstrates that decision
  and effect outcomes can disagree and that the harness finds synthetic cut
  sets. It provides no population or cross-system estimate.

### Cycle 2 — 2026-09-24

- **Review:** selected incomplete E0 oracle semantics as the highest blocker
  that could be resolved without a Kubernetes runtime.
- **Fix:** extended effect records with completion and compensation identity;
  added recovery-observation traces and oracle outputs for partial effects,
  independently confirmed rollback, delayed regression, and stale observation.
  The first rollback fixture exposed that compensation actions were being
  counted as fresh unsafe effects; the evaluator was corrected before commit.
- **Run:** 133 unit/regression tests and all SENTINEL lint checks passed. The
  nine-trial smoke campaign retained its prior four unauthorized effects, one
  observation disagreement, and safe-recovery summary.
- **Analyze:** the E0 semantic oracle contract now covers the planned terminal
  classes without reading the guardrail verdict or tool-return status. This is
  harness evidence only; timing windows and signals remain unvalidated on live
  systems.

### Cycle 3 — 2026-09-25

- **Review:** selected the missing schema/allowlist comparison, the highest P0
  blocker that did not require a live cluster.
- **Fix:** added an explicitly limited baseline that validates exact proposal
  shape, capability, argument types, and a static resource allowlist but has no
  incident-specific trusted binding. Added a frozen six-trial matrix replaying
  identical nominal and wrong-service proposals across no guard, static
  schema/allowlist, and Guardian, plus per-guardrail summaries.
- **Run:** 138 unit/regression tests and all SENTINEL lint checks passed. The
  immutable `e1-baseline-smoke-v1` simulator run completed.
- **Analyze:** in the two trials per condition, Guardian contained the injected
  wrong-service proposal (0/2 unauthorized), whereas no guard and the static
  schema/allowlist each produced one unauthorized effect (1/2). All three
  recovered safely in their nominal trial. These are deterministic contract
  examples, not rate estimates or evidence of population superiority.

### Cycle 4 — 2026-09-25

- **Review:** selected protocol freezing because unversioned operator semantics
  and outcome-dependent analysis choices would invalidate later experiments.
- **Fix:** froze a machine-readable v1 catalog for all 11 implemented operators,
  including mutations, expected relations, and paired preconditions. Froze five
  primary contrasts plus experimental unit, systems, baselines, outcomes,
  exclusions, non-exclusions, pairing, randomization, and multiplicity rules.
  Added executable contract coverage for every operator.
- **Run:** 153 unit/regression tests and all SENTINEL lint and JSON syntax checks
  passed. An initial protocol-status spelling mismatch was caught and corrected.
- **Analyze:** operator and primary-analysis semantics are now protected from
  silent post-outcome changes. This is an internal frozen protocol, not a public
  timestamped preregistration; sample size and interval model remain explicitly
  deferred to the blinded infrastructure pilot.

### Cycle 5 — 2026-09-25

- **Review:** selected the pairwise design because an informal hand-picked
  campaign would leave interaction coverage ambiguous and make trial budgeting
  impossible.
- **Fix:** added a deterministic generator and coverage verifier producing one
  nominal row, all 11 single operators, and all 46 exact cross-layer operator
  pairs. The generated design is content-digested and checked into the protocol.
  Design review exposed that contrast C5 named an always-deny baseline absent
  from the frozen guardrail list; the protocol was corrected before execution.
- **Run:** the generator produced 58 unique rows with 46/46 required pairs
  covered and a budget of 580 trials per repetition across two systems and five
  guardrails. All 157 tests and lint checks passed.
- **Analyze:** exhaustive cross-layer pair coverage is feasible without a full
  320-cell layer-factorial. Repetition count remains unset until the blinded
  pilot; the 580-trial base budget excludes resets, reruns, and cut-set
  minimization and therefore is not yet a runtime estimate.

## Next highest-priority cycle

Implement the always-deny sanity baseline and an external-policy adapter with a
strictly equivalent rule set. Validate both on the frozen proposal pairs and
record semantic-equivalence tests before expanding the 58-row design into
concrete system/guardrail trials.
