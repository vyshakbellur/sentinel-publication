# SENTINEL publication-readiness ledger

Last reviewed: 2026-09-24

Iteration budget: **2/25 completed**. Stop after Cycle 25, or earlier if every
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
| Frozen threat model and fault catalog | Partial | Six-layer taxonomy exists, but operators and exclusions are not preregistered/frozen. |
| Meaningful baselines | Fail | Only Guardian and no-guard simulator paths exist; schema/allowlist and OPA/Cedar are missing. |
| First realistic public system | Fail | Online Boutique is revision-locked but not deployed or actuated by SENTINEL. |
| Second realistic public system | Fail | OTel Demo is revision-locked but not deployed or actuated by SENTINEL. |
| Repeated trials and uncertainty | Fail | Current evidence is nine deterministic smoke trials; no confirmatory sampling or intervals. |
| Cross-layer interaction analysis | Partial | One synthetic two-fault cut set is reproduced; no covering array or live-system confirmation. |
| Ablations | Fail | Planned but not executed. |
| Clean-environment artifact reproduction | Fail | Unit suite passes locally; no clean-machine/container reproduction report. |
| Anonymous venue package | Fail | Markdown draft only; no DSN template, anonymized artifact, or generated figures. |

## Critical reviewer findings

### P0 — Claims exceed evidence

The draft proposes a multi-system empirical study but currently contains no
realistic-system results. The nine-trial simulator result must be labeled E0 and
must never populate the confirmatory result tables.

### P0 — Missing comparisons

No schema/allowlist or external policy baseline is implemented. Without at
least one non-Guardian deterministic baseline, reviewers cannot separate the
methodology's value from implementation-specific behavior.

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

## Next highest-priority cycle

Implement the schema/allowlist baseline behind the same guardrail interface and
replay the frozen smoke matrix across no-guard, schema/allowlist, and Guardian.
The comparison must expose trusted-binding differences without implying
population results. After that, freeze the fault catalog and primary contrasts.
