# SENTINEL publication-readiness ledger

Last reviewed: 2026-09-24

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
| Independent oracle fixtures | Partial | Seven deterministic effect/recovery fixtures added; delayed regression, rollback, and partial-effect fixtures remain. |
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

### P1 — Oracle independence is incomplete

The effect oracle is now a separate function that receives neither policy
verdict nor tool-return success. Remaining fixtures must cover partial effects,
rollback confirmation, delayed regression, and observer staleness.

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

## Next highest-priority cycle

Complete E0 by adding explicit partial-effect, rollback, delayed-regression,
and stale-observer contracts and fixtures. Then implement the schema/allowlist
baseline before beginning Kubernetes integration. A live experiment should not
start until the oracle can distinguish these terminal states reliably.
