# SENTINEL publication-readiness ledger

Last reviewed: 2026-09-25

Iteration budget: **13/25 completed**. Stop after Cycle 25, or earlier if every
publication gate passes. The final cycle must record a readiness verdict and
all remaining blockers before pausing the publication automation.

## Current verdict

**Not publishable as a research paper.** The novelty claim and experimental
protocol are credible, but the evidence supports only a simulator/harness
demonstration. The abstract, results, and conclusion still contain placeholders.

Current maturity: **frozen protocol + simulator preflight + live contracts**.

## Release gates

| Gate | Status | Evidence or blocker |
|---|---|---|
| Defensible novelty statement | Pass | Effect-grounded cross-layer guardrail evaluation; does not claim deterministic enforcement itself as new. |
| Complete manuscript without placeholders | Fail | Abstract, results tables, discussion, and conclusion await confirmatory results. |
| References verified against primary sources | Partial | Seventeen core entries now have primary-source metadata, claim limits, and matching BibTeX; 15 candidate entries remain unverified. |
| Independent oracle fixtures | Pass | Eleven deterministic fixtures cover safe/no-effect, wrong target, duplicate identity and semantic effects, excessive and partial effects, false success, rollback, delayed regression, and stale observation. Live calibration remains separate. |
| Frozen threat model and fault catalog | Pass | Versioned machine-readable v1 catalog declares all 11 implemented operators; five primary contrasts, exclusions, non-exclusions, pairing, and analysis rules are frozen before live-pilot outcomes. |
| Meaningful baselines | Partial | No-guard, schema/allowlist, Guardian, checksum-pinned OPA, and always-deny now run on frozen simulator proposals; live-system equivalence remains. |
| First realistic public system | Fail | Online Boutique has a revision-locked target, least-privilege RBAC, and a readiness gate, but has not been deployed or actuated. |
| Second realistic public system | Fail | OTel Demo and its official Helm chart have a revision-locked target, least-privilege RBAC, and a readiness gate, but have not been deployed or actuated. |
| Repeated trials and uncertainty | Fail | Exact binomial intervals and paired-contrast extraction are implemented for descriptive preflight analysis, but there are no repeated live trials, pilot variance, or confirmatory intervals. |
| Cross-layer interaction analysis | Partial | The 58-row design expanded to 580 unique system/guardrail rows and completed a simulator preflight; live execution, repetitions, and inferential analysis remain. |
| Ablations | Fail | Planned but not executed. |
| Clean-environment artifact reproduction | Fail | Unit suite passes locally; no clean-machine/container reproduction report. |
| Anonymous venue package | Fail | Markdown draft only; no DSN template, anonymized artifact, or generated figures. |

## Critical reviewer findings

### P0 — Claims exceed evidence

The draft proposes a multi-system empirical study but currently contains no
realistic-system results. The nine-trial simulator result must be labeled E0 and
must never populate the confirmatory result tables.

### P0 — Missing comparisons

The OPA and always-deny baselines are integrated for simulator studies, but
their rule equivalence and safety–recovery behavior have not been validated on
the two live systems. Simulator agreement cannot establish external validity.

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

The 17-reference core is verified against publisher, proceedings, government,
or arXiv records and has a checked `.bib` database. Fifteen candidate works
still need primary-source verification and publication-status checks before
they can support final novelty claims.

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

### Cycle 6 — 2026-09-25

- **Review:** selected the missing external-policy and always-deny baselines,
  which blocked contrasts C2 and C5 and left Guardian-specific effects
  inseparable from methodology effects.
- **Fix:** integrated checksum-pinned Open Policy Agent v1.21.0 with a Rego v1
  rule over the same trusted scope and proposal vocabulary, added a portable
  tool lock/fetcher, and added the always-deny sanity condition. Added matched
  Guardian/OPA semantic tests and a ten-trial five-condition smoke matrix.
- **Run:** OPA's own policy checker passed; all 160 tests ran with OPA enabled,
  and SENTINEL lint checks passed. The immutable
  `e2-policy-baseline-smoke-v1` run completed.
- **Analyze:** on one nominal and one wrong-service contract example per
  condition, Guardian and OPA matched (0/2 unauthorized, 1/2 safe recovery),
  schema/allowlist and no guard each allowed the wrong target (1/2
  unauthorized), and always-deny prevented all effects but recovered 0/2.
  This validates comparison semantics and the need for a joint safety–recovery
  metric; it is not a rate estimate or live-system result.

### Cycle 7 — 2026-09-25

- **Review:** selected campaign expansion because row-level coverage did not yet
  guarantee unique identities, balanced system/guardrail allocation, or reset
  metadata in a runnable study.
- **Fix:** added deterministic expansion of the 58-row design across two system
  labels and five guardrails, yielding 580 unique trial IDs with an explicit
  restoration fixture per row. Added a prominent simulator-boundary marker and
  moved forged-authority mutation upstream so all guardrails receive the same
  proposal transformation.
- **Run:** all 164 tests and lint checks passed. The immutable
  `e3-campaign-preflight-v1` executed all 580 rows, wrote 580 terminal records,
  and generated 232 minimized outcome findings without missing or duplicate
  trial IDs.
- **Analyze:** the selected synthetic campaign produced 172 unauthorized
  effects and 60 observation disagreements. Even always-deny had four unsafe
  effects when paired enforcement-bypass scenarios overrode its decision.
  These counts validate end-to-end fault plumbing and show why decision-only
  metrics are insufficient; because rows are deliberately selected and the two
  “systems” share one simulator vocabulary, none is a field-risk estimate or
  cross-system result.

### Cycle 8 — 2026-09-25

- **Review:** selected analysis integrity because campaign outputs could not yet
  be verified or safely separated from confirmatory evidence by software.
- **Fix:** added manifest, record, spec-digest, and unique-ID verification;
  Clopper–Pearson intervals; paired extraction for C1, C2, and C5; and a hard
  rejection path preventing simulated incidents from entering confirmatory
  analysis. Added a reproducible preflight report with explicit limitations.
- **Run:** all 169 tests, including OPA integration, and all lint checks passed.
  All 580 E3 records and their manifest/spec digests verified. The checked-in
  analysis regenerates byte-equivalent structured results from those records.
- **Analyze:** paired selected-row contrasts show the pipeline can recover the
  intended comparison structure, but the report labels every interval as
  descriptive because configurations are deliberately selected and both system
  labels use one simulator. The tooling now refuses `--confirmatory` analysis
  for this run rather than relying on author discipline.

### Cycle 9 — 2026-09-25

- **Review:** selected the live execution boundary because Kubernetes work could
  not safely begin without explicit separation of mutation, observation, and
  reset authority or revision-correct workload names.
- **Fix:** added Kubernetes actuator and read-only observer adapters with
  separate contexts, strict deployment-state parsing, convergence checks, and
  a deterministic reset contract. Added pinned mappings for Online Boutique
  `adservice`/`cartservice` and OTel Demo `ad`/`cart`; pinned the official OTel
  Demo Helm chart at release 0.42.0 and documented the architecture/trade-offs.
- **Run:** 174 tests and all lint/JSON checks passed using recorded Kubernetes
  responses for both systems. Tests verify command boundaries, context
  separation, replica validation, deterministic restoration, convergence, and
  mapping-to-lock consistency.
- **Analyze:** the live boundary is now implementable without allowing the
  actuator or guardrail to define its own success. This remains contract and
  fixture evidence: no API server, controller race, rollout delay, RBAC policy,
  or health signal has been exercised.

### Cycle 10 — 2026-09-25

- **Review:** selected trial lifecycle enforcement because individual actuator
  and observer calls did not guarantee pre-state capture, mandatory cleanup, or
  a terminal record when execution fails.
- **Fix:** added a fail-safe live-trial state machine that captures only a
  converged baseline, injects and independently observes the incident, applies
  an allowed bounded action, infers effects from state differences, evaluates
  the independent oracle, and restores/verifies the environment in `finally`.
  Terminal records include ordered phases, errors, effects, oracle output,
  restoration status, and a stable digest.
- **Run:** 180 tests and all lint checks passed. Stateful recorded transports
  exercised safe recovery, blocked safe failure, wrong-target effects, both
  workload vocabularies, and a seeded actuator exception. The exception still
  restored and independently verified the original state.
- **Analyze:** cleanup and observer independence are now state-machine
  invariants rather than runbook conventions. Immediate-convergence recorded
  transports cannot validate Kubernetes controller lag, concurrent mutation,
  API retries, or real recovery windows.

### Cycle 11 — 2026-09-25

- **Review:** selected deployment authorization and preflight readiness because
  separate context names alone did not prove separate authority, least
  privilege, target presence, or safe starting state.
- **Fix:** added namespace bootstrap and resource-name-scoped RBAC for distinct
  observer and actuator service accounts on both workloads. Added a read-only,
  fail-closed readiness checker that verifies distinct contexts, positive and
  negative authorization, mapped target availability, convergence, and a
  content-digested report. Added an operational checklist with explicit stop
  and rollback triggers.
- **Run:** 185 tests, all lint checks, and JSON syntax validation passed.
  Recorded transports exercised the ready path, shared-context rejection,
  excess observer authority, unconverged targets, exact authorization command
  construction, and static manifest scope. No live API server was contacted.
- **Analyze:** context separation and bounded permissions are now executable
  admission criteria rather than deployment assumptions. Fixture-backed
  authorization responses do not establish that a real cluster honors the
  manifests, that service-account contexts are correctly issued, or that the
  pinned applications converge.

### Cycle 12 — 2026-09-25

- **Review:** selected the missing single-row live controller because the
  adapters, readiness gate, decision baselines, and restoration state machine
  still required manual composition that could bypass the frozen protocol or
  lose pre-capture failures.
- **Fix:** added a uniform decision boundary for all five frozen guardrails and
  refactored simulator execution through it. Added a one-row live-pilot command
  that validates system and guardrail membership against the frozen protocol,
  reruns readiness before mutation, binds the decision to the fail-safe trial,
  records protocol/readiness digests, captures decision and pre-state failures,
  and uses durable exclusive file creation to prevent evidence overwrite.
- **Run:** 190 tests and all lint checks passed. Recorded transports exercised
  successful mutation and restoration, shared-context rejection with zero
  cluster calls, a pre-capture observation failure with zero mutations,
  rejection of an unfrozen guardrail, and refusal to overwrite an existing
  record. The command help path also ran successfully.
- **Analyze:** the first live pilot row is now executable without manual glue,
  and failure paths yield auditable terminal evidence. This remains contract
  evidence: no Kubernetes runtime was available, so controller timing, RBAC
  enforcement, workload convergence, and live guardrail behavior remain
  unmeasured.

### Cycle 13 — 2026-09-25

- **Review:** selected reference integrity because the related-work argument
  depended on a prose candidate list containing mixed preprints, proceedings,
  and two incorrect or incomplete venue/title descriptions.
- **Fix:** verified 17 core references against primary publisher, proceedings,
  government, or arXiv records; added a structured ledger with publication
  status and per-work claim limits; created matching BibTeX; and added a
  fail-closed ledger/BibTeX integrity checker. Corrected Conformal Risk Control
  to ICLR 2024, AIOpsLab to MLSys 2025, and the NASA runtime-assurance title and
  year. Added the previously omitted ToolGate paper and explicit differentiation
  in related work.
- **Run:** the reference checker validated 17 unique identifiers and exact
  citekey parity; 192 tests, all lint checks, and JSON syntax validation passed.
  The negative test proves duplicate identifiers fail closed; exact citekey-set
  equality guards ledger/BibTeX drift.
- **Analyze:** ToolGate is closer prior art than the draft acknowledged because
  it combines preconditions with runtime-verified postconditions. The defensible
  SENTINEL claim is therefore narrower: cross-layer fault injection and
  independent environment-effect evaluation of an assurance chain, not action
  contracts, postconditions, or deterministic enforcement. Preprints remain
  labeled as preprints, and the remaining 15 candidates are not yet verified.

## Next highest-priority cycle

The P0 experimental blocker remains a disposable Kubernetes runtime with
`kubectl` and Helm. While it is unavailable, verify or remove the 15 remaining
candidate references, prioritizing the closest authorization, durable-effect,
and autonomous-remediation papers; then make every related-work claim resolve
to a checked citation key.
