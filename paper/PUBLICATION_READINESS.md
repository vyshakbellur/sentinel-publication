# SENTINEL publication-readiness ledger

Last reviewed: 2026-09-26

Iteration budget: **25/25 completed**. The hard cycle budget is exhausted and
the publication automation is paused. Resume only after the required live
environment or another explicitly authorized scope change is available.

## Current verdict

**FINAL VERDICT: not publishable as a research paper.** The novelty claim and experimental
protocol are credible, but the evidence supports only a simulator/harness
demonstration. The abstract, results, and conclusion still contain placeholders.

Current maturity: **complete pilot and audit-reconciliation contracts + simulator preflight/ablations; no live run**.

Automation status: **PAUSED AT CYCLE 25**.

## Release gates

| Gate | Status | Evidence or blocker |
|---|---|---|
| Defensible novelty statement | Pass | Effect-grounded cross-layer guardrail evaluation; does not claim deterministic enforcement itself as new. |
| Complete manuscript without placeholders | Fail | The audit finds eight result tokens, 35 result-table cells, and 15 open release-checklist items; abstract, results, discussion, and conclusion await confirmatory evidence. |
| References verified against primary sources | Pass | All 31 retained references have primary-source metadata, explicit publication status and claim limits, matching BibTeX, and checked manuscript citekeys. |
| Independent oracle fixtures | Pass | Eleven deterministic fixtures cover safe/no-effect, wrong target, duplicate identity and semantic effects, excessive and partial effects, false success, rollback, delayed regression, and stale observation. Live calibration remains separate. |
| Frozen threat model and fault catalog | Pass | Versioned machine-readable v1 catalog declares all 11 implemented operators; five primary contrasts, exclusions, non-exclusions, pairing, and analysis rules are frozen before live-pilot outcomes. |
| Meaningful baselines | Partial | No-guard, schema/allowlist, Guardian, checksum-pinned OPA, and always-deny now run on frozen simulator proposals; live-system equivalence remains. |
| First realistic public system | Fail | Online Boutique has a revision-locked target, least-privilege RBAC, and a readiness gate, but has not been deployed or actuated. |
| Second realistic public system | Fail | OTel Demo and its official Helm chart have a revision-locked target, least-privilege RBAC, and a readiness gate, but have not been deployed or actuated. |
| Repeated trials and uncertainty | Fail | The independent deployment/incident/load block and a 19-row powered confirmatory subset are preregistered, but there are no repeated live trials, pilot variance, frozen repetition count, or confirmatory intervals. |
| Cross-layer interaction analysis | Partial | The 58-row descriptive census is separated from seven prespecified all-layer confirmatory pairs; live execution, repeated independent blocks, and inferential analysis remain. |
| Ablations | Partial | Trusted-scope and fail-closed mechanism ablations completed on all 58 selected simulator rows; independent-observer and broker-idempotency ablations still require live execution. |
| Clean-environment artifact reproduction | Partial | A second fresh CPython 3.12 environment reproduced the expanded 234-test artifact, lint, OPA integration, and citation checks from frozen locks; it is still the same host and does not exercise Kubernetes. |
| Anonymous venue package | Partial | Anonymous metadata, artifact appendix, and machine-checked claim/evidence ledger exist, but the venue template, live records, figures, sanitized archive, and supported result claims are absent. |

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
live systems before confirmatory use. Broker duplicate-attempt receipts also
require reconciliation with independent Kubernetes API audit events.

### Resolved in Cycle 14 — Manuscript/reference integrity

All 31 retained references are verified against publisher, proceedings,
government, or arXiv records and have a checked `.bib` database. Publication
status is explicit, and manuscript citation keys fail closed if absent from the
ledger. The redundant RACER candidate was removed rather than used to support a
claim.

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

### Cycle 14 — 2026-09-25

- **Review:** selected the 15 remaining bibliography candidates because the
  final novelty and related-work argument could not safely cite them while
  venue status and metadata were unresolved.
- **Fix:** verified 14 against primary arXiv or conference records, added their
  authorship, status, identifiers, relevance, and claim limits to the ledger and
  BibTeX, and removed the redundant RACER candidate rather than relying on it.
  Added checked citation keys throughout related work and extended validation
  so unknown manuscript keys fail closed.
- **Run:** the reference checker validated exact parity across 31 ledger and
  BibTeX entries and resolved every manuscript citation key. All 193 tests,
  lint checks, and JSON checks passed, including a negative unknown-citation
  test.
- **Analyze:** AGENTCHAOSBENCH is the closest fault-injection methodology but
  targets telemetry-based fault detection/localization; ToolGate is the closest
  contract/postcondition mechanism. SENTINEL remains differentiated only by
  measuring containment and recovery under cross-layer faults with an
  independent environment-effect oracle. Most 2025–2026 neighbors are
  preprints, now labeled as such rather than presented as peer-reviewed work.

### Cycle 15 — 2026-09-25

- **Review:** selected clean-environment reproducibility because prior test
  evidence reused project-external virtual environments and had no frozen
  dependency graph or machine-readable reproduction report.
- **Fix:** froze the complete Python runtime/test dependency graph, added a
  one-command verifier that creates a temporary virtual environment, installs
  from the constraint lock, fetches the checksum-pinned OPA binary, runs tests,
  lint, and reference checks, and emits lock/source digests with explicit
  limitations. Documented the workflow and excluded generated editable-install
  metadata.
- **Run:** the first fresh-environment attempt failed one report-equivalence
  test with SciPy 1.18.1/NumPy 2.5.3 because exact Clopper–Pearson interval
  serialization changed. Pinning the analysis stack to SciPy 1.13.1 and NumPy
  1.26.4 restored byte-equivalent analysis. The second fresh CPython 3.12.7 run
  passed all 193 tests, lint, OPA 1.21.0 integration, and 31-reference checks;
  its report and digests are checked in.
- **Analyze:** analysis-library drift can change exact interval values and the
  derived report digest without changing experiment records, so dependency
  versions are part of the evidence chain. A fresh virtual environment on this
  host is stronger than the previous reused-environment result but is not an
  independent clean-machine or container reproduction and does not exercise
  Kubernetes.

### Cycle 16 — 2026-09-26

- **Review:** selected missing guardrail ablations, the highest unresolved gate
  that could be advanced without repeatedly probing the unavailable Kubernetes
  runtime. Review also separated mechanism sensitivity from confirmatory effect
  estimation so deterministic selected rows cannot be mistaken for samples.
- **Fix:** added explicit Guardian variants that remove incident-specific
  trusted target binding or replace validation fail-closed behavior with a
  permissive proposal-target fallback. Added a versioned exploratory ablation
  protocol, balanced 174-row campaign construction over the frozen 58-row
  fault design, paired integrity analysis, CLI support, contract tests, and
  manuscript language reserving observer and broker ablations for the live
  boundary.
- **Run:** the immutable `e4-guardian-ablation-preflight-v1` run wrote 174
  terminal records: 58 matched selected rows for full Guardian and each of the
  two variants. Manifest/spec/record verification passed; all 197 tests passed
  with checksum-pinned OPA enabled, scoped lint passed, and all 31 reference
  records revalidated.
- **Analyze:** full Guardian produced 10 unauthorized effects and 10 safe
  recoveries across the 58 selected rows. Removing trusted scope binding
  produced 19 unauthorized effects with no additional safe recoveries: nine
  matched rows became newly unsafe. Permissive fallback produced 22
  unauthorized effects and 19 safe recoveries: 12 rows became newly unsafe and
  nine gained safe recovery. These deterministic counts demonstrate that the
  harness detects the intended containment/availability trade-off; they are
  not rates, uncertainty-bearing estimates, live-system results, or evidence
  that either mechanism has the same effect in deployed systems.

### Cycle 17 — 2026-09-26

- **Review:** selected the unresolved statistical-design blocker that could be
  advanced without Kubernetes. The prior plan risked treating all 580 selected
  cells per repetition as an inferential sample and counting repeated calls on
  an unchanged deployment as independent evidence.
- **Fix:** froze a phase-disjoint study partition before live outcomes: a
  guardrail-label-blinded 12-row pilot, a descriptive 58-row fault-surface
  census, and a powered 19-row confirmatory subset. The subset retains nominal
  and all 11 single faults plus seven mechanism-motivated pairs spanning all
  six layers; every selected pair's component singles are present. Defined an
  independent block as deployment instance crossed with incident template and
  load seed, prohibited record reuse across phases, added machine-readable run
  prefixes and rerun rules, and aligned the manuscript and DSN plan.
- **Run:** the partition audit verified the frozen design and protocol digests,
  row membership, pair rationales, component-single support, all-layer
  representation, and phase separation. It computed complete-block budgets of
  120 pilot cells, 580 census cells, and 190 confirmatory cells. All 200 tests
  passed with checksum-pinned OPA enabled, scoped lint passed, and all 31
  references revalidated.
- **Analyze:** the revision converts the 580-cell design into a coverage census
  rather than a source of pseudo-replicated confidence intervals. Only the
  independently blocked 19-row study may support C1--C5, with repetitions and
  power still unset until a blinded live pilot. The seven pairs test
  prespecified assurance pathways rather than every interaction, so omitted
  pairs remain descriptive and the paper cannot yet make inferential claims.

### Cycle 18 — 2026-09-26

- **Review:** selected enforcement of the new pilot/census/confirmatory
  partition because prose-only phase separation could still allow exploratory
  records into primary analysis or label nominal live actions as fault trials.
- **Fix:** bound the single-row live controller to a phase, frozen design row,
  deployment instance, incident template, and load seed. The controller now
  enforces phase-specific trial-ID prefixes and row allocation; records carry
  protocol, design, partition, and independent-block digests plus explicit
  confirmatory eligibility. Confirmatory execution fails closed while the
  repetition count is pending. Primary-analysis validation recomputes record
  digests and rejects pilot/census records or mismatched evidence-chain
  digests. Non-nominal rows fail before cluster access because live fault
  adapters do not yet exist.
- **Run:** all 206 tests passed with checksum-pinned OPA enabled, scoped lint
  passed, all 31 references revalidated, and the expanded live-pilot CLI help
  path executed. Recorded transports exercised a phase-bound nominal trial and
  restoration, rejected a non-nominal row with zero cluster commands, rejected
  a wrong phase prefix, kept confirmatory execution locked, rejected pilot
  evidence from primary analysis, and detected record tampering.
- **Analyze:** the artifact now enforces the Cycle 17 statistical boundary
  rather than relying on author discipline. This prevents evidence leakage and
  false fault labels but adds no live-system outcome, variance estimate, or
  confirmatory result. Only nominal `PW000` can currently cross the live
  boundary; the remaining 11 pilot rows require real fault injection semantics.

### Cycle 19 — 2026-09-26

- **Review:** selected the missing single-fault live adapters that could be
  implemented faithfully without a Kubernetes chaos operator. The controller
  previously rejected every non-nominal row, leaving the 12-row pilot design
  mostly non-executable.
- **Fix:** added controller-level applications for stale evidence, wrong
  predictor target, cross-tenant binding, forged authority, stale manifest,
  overbroad policy scope, and false-success observation. Evidence/predictor
  faults deterministically select the alternate frozen Deployment; binding and
  policy faults reach the real decision adapter; false success changes only the
  claimed-recovery channel while preserving the independent environment
  observer. Terminal v3 records bind requested faults to the applied proposal,
  decision faults, and observation override. Conflicting manual proposal
  overrides fail closed. The four enforcement operators remain unsupported and
  are rejected before cluster access.
- **Run:** all 215 tests passed with checksum-pinned OPA enabled, scoped lint
  passed, and all 31 references revalidated. Recorded transports exercised all
  seven new single-fault adapters: stale evidence and wrong prediction produced
  independently detected wrong-target effects under no guard; all three
  binding faults made Guardian fail closed with no remediation effect;
  overbroad policy preserved the nominal single-row outcome; and false success
  created an observation disagreement without changing environment truth.
  Restoration succeeded in every executed contract trial.
- **Analyze:** nominal plus seven controller-level singles now have auditable
  live execution contracts, covering 8 of the 12 pilot rows. These are mocked
  transport contract results, not Kubernetes executions or safety-rate
  estimates. Argument substitution, bypass, dropped effect, and duplicate retry
  require broker/action-receipt instrumentation; implementing them as labels or
  ordinary replica calls would invalidate the fault semantics.

### Cycle 20 — 2026-09-26

- **Review:** selected the four missing enforcement single-fault adapters,
  which blocked complete pilot-row execution and could not be graded faithfully
  from final replica state alone, especially for an idempotent duplicate write.
- **Fix:** added per-attempt broker execution receipts recording semantic action
  identity, requested and executed targets, attempt number, submission,
  completion, bypass, and drop status. Implemented post-decision argument
  substitution, denied-action bypass, pre-submission drop, and two-attempt
  duplicate retry. Environment state remains authoritative for wrong target and
  recovery; the oracle uses completed broker receipts only to detect semantic
  duplicate attempts that converge to one final state. Live terminal records
  now preserve both receipts and independently observed effects.
- **Run:** all 223 tests passed with checksum-pinned OPA enabled, scoped lint
  passed, and all 31 references revalidated. Recorded transports showed
  argument substitution producing a wrong-target effect and mismatched
  requested/executed receipt; bypass submitting a blocked action; drop leaving
  the incident safely unrecovered without API submission; and duplicate retry
  producing two completed receipts, one final state transition, and an unsafe
  duplicate classification. Each trial restored its captured state.
- **Analyze:** all 12 pilot rows now have executable controller contracts.
  Receipt-aware grading closes the idempotent-final-state blind spot, but the
  receipts are produced by the experiment broker and have not been reconciled
  with an independent API-server audit trail. The results remain mocked
  transport contract evidence, not proof that Kubernetes accepted the same
  attempts, live-system rates, or confirmatory findings.

### Cycle 21 — 2026-09-26

- **Review:** selected missing blocked randomization and batch safety because
  individually executable rows did not guarantee a complete pilot, unique
  cells, independent blocks, label blinding, or a halt after restoration
  failure.
- **Fix:** added a content-digested scheduler that expands the frozen 12-row
  pilot across two systems, five guardrails, and three declared independent
  deployment/load blocks. Within each system/block, SHA-256 ordering keys
  deterministically randomize 60 cells. The audit enforces unique trial IDs,
  exactly one copy of every block/system/guardrail/row cell, contiguous order,
  valid phase bindings, and matching protocol/design/partition digests. Added a
  keyed analyst projection that removes guardrail labels and ordering keys, and
  a batch executor that stops after the first unsuccessful terminal record.
- **Run:** generated and checked the explicitly non-executable
  `pilot_schedule_contract`: 360 unique cells, six system blocks, 60 rows per
  system block, and three repetitions of each system/guardrail/row cell. The
  blinded projection produced 360 unique condition tokens without labels or
  randomization keys; a seeded failure stopped the executor after the second of
  three test rows. All 226 tests passed with checksum-pinned OPA enabled,
  scoped lint passed, and all 31 references revalidated.
- **Analyze:** the planned pilot is now operationally complete and resistant to
  missing-cell, duplicate-cell, phase-leakage, and outcome-reordering errors.
  The checked schedule uses placeholder deployment identifiers and was not
  executed; its three repetitions are design blocks, not observed variance or
  a confirmatory sample size. Real block identifiers, cluster state, outcomes,
  and analyst/operations key separation remain absent.

### Cycle 22 — 2026-09-26

- **Review:** selected the unresolved independence of broker receipts. A
  duplicate retry can converge to the same environment state as one write, but
  trusting the experiment broker's own attempt count would make the safety
  claim circular.
- **Fix:** attached a unique deterministic `sentinel-*` field-manager
  correlation to each submitted scale attempt and added strict parsing for
  Kubernetes `audit.k8s.io/v1` `ResponseComplete` Deployment scale events.
  Reconciliation requires exact correlation, dedicated actuator identity,
  namespace, target, replica value, verb, completion status, unique audit ID,
  and a one-to-one receipt/event multiset; missing or extra events fail closed.
  Added a write-once reconciliation command, a scale-only API-server audit
  policy, known-event fixtures, and pilot operating instructions.
- **Run:** all 234 tests passed with checksum-pinned OPA enabled, scoped lint
  passed, all 31 references revalidated, and the live-pilot help path ran.
  Fixtures demonstrated one receipt/one event agreement, two uniquely
  correlated audit events for a semantic duplicate, successful no-event
  reconciliation for a dropped pre-submission action, and rejection of missing,
  extra, uncorrelated, non-scale, tampered-record, and wrong-actor evidence.
- **Analyze:** the artifact can now distinguish an idempotent duplicate write
  from one write without relying solely on broker self-report. This is fixture
  contract evidence only: the host still lacks Kubernetes, the proposed audit
  policy is not enabled, `kubectl scale` correlation propagation is not
  empirically observed, and no real API audit event has been reconciled.

### Cycle 23 — 2026-09-26

- **Review:** selected stale clean-environment evidence because the Cycle 15
  report covered 193 tests and predated the study partition, all live fault
  adapters, scheduler, and audit reconciliation.
- **Fix:** reused the frozen CPython dependency graph and checksum-pinned OPA
  bootstrap to construct a new temporary virtual environment from scratch and
  emitted a new content-described reproduction report for the expanded source
  tree.
- **Run:** CPython 3.12.7 created the temporary environment, installed the
  complete constraint lock, fetched and verified OPA 1.21.0, passed all 234
  tests, passed scoped lint, and revalidated all 31 references.
  Every recorded command exited zero. The report records dependency/tool/source
  digests, command tails, timings, platform, and explicit limitations.
- **Analyze:** the expanded non-live artifact remains reproducible from frozen
  inputs in a fresh environment, and no new dependency drift appeared after
  the exact SciPy/NumPy pins introduced in Cycle 15. This is a second virtual
  environment on the same macOS host—not an independent machine, container
  attestation, Kubernetes deployment, or replication of empirical results—so
  the reproduction gate remains partial.

### Cycle 24 — 2026-09-26

- **Review:** selected the missing anonymous package and claim-control boundary.
  With no live evidence, packaging work had to make unsupported claims harder
  to publish rather than cosmetically converting the draft into a venue paper.
- **Fix:** created anonymous metadata, an artifact-appendix skeleton, and a
  machine-readable claim/evidence ledger with explicit permitted and prohibited
  wording. Added fail-closed checks for the eight required claim classes,
  artifact existence, duplicate claims, missing claims marked assertable, local
  identity markers, unresolved manuscript placeholders, open release gates,
  and the absence of a venue template. The package declares itself blocked and
  cannot certify submission readiness.
- **Run:** the package audit found two supported claims, three partial claims,
  and three missing claims; six claim classes remain unresolved. It counted
  eight abstract/conclusion result tokens, 35 result-table placeholders, and 15
  open publication-gate items, with no venue template. All 236 tests passed
  with checksum-pinned OPA enabled, scoped lint passed, and all 31 references
  revalidated.
- **Analyze:** the skeleton is anonymous and useful for reviewer-facing claim
  discipline, but it is intentionally not a submission. It prevents simulator
  or fixture evidence from being described as two-system safety results and
  records the precise missing evidence. No result placeholder was filled, no
  figure was fabricated, and the anonymous-package gate advances only to
  partial.

### Cycle 25 — 2026-09-26 — terminal reviewer audit

- **Review:** conducted the required terminal audit against every release gate,
  the claim/evidence ledger, manuscript placeholders, latest simulator and
  contract results, reproduction report, references, and clean repository
  state. The audit confirmed that methodological preparation cannot substitute
  for the absent two-system live study.
- **Fix:** added a machine-readable final verdict containing supported claims,
  prohibited current claims, exact critical blockers, required user input, and
  the ordered resumption path. Marked the 25-cycle budget exhausted and the
  automation paused; no result placeholder or readiness status was upgraded
  without evidence.
- **Run:** all 236 current tests passed with checksum-pinned OPA enabled, scoped
  lint passed, and all 31 references revalidated. The anonymous-package audit
  again reported `submission_ready: false`, with two supported, three partial,
  and three missing claim classes, eight result tokens, 35 empty result cells,
  15 open release items, and no venue template. Cycle 23 remains the latest
  fresh-environment report and covered all 234 tests present at that point.
- **Analyze:** SENTINEL is a strong pre-results methodology and artifact, not a
  publishable empirical research paper. The differentiating hypothesis is
  defensible and the experimental boundary is unusually well controlled, but
  the central claims require live effects, independent blocks, uncertainty,
  cross-system transfer, and calibrated audit/oracle evidence. Further local
  scaffolding has sharply diminishing publication value. The scientifically
  correct next action is to stop automation and obtain the live environment.

## Final remaining blockers and resumption conditions

1. **User/environment input required:** attach a dedicated disposable
   Kubernetes cluster with `kubectl`, Helm, administrator access for setup,
   separate observer/actuator contexts, and retrievable RequestResponse audit
   events for `deployments/scale`. Production clusters are out of scope.
2. Deploy and smoke-test the pinned Online Boutique and OTel Demo subjects;
   preserve readiness, RBAC, restoration, and audit-reconciliation records.
3. Supply three independent deployment/load blocks per system, execute the
   blinded 360-cell pilot, and freeze recovery windows, repetition count,
   power assumptions, and statistical model without evaluating C1--C5.
4. Execute the 580-cell descriptive census and the powered 190-cell-per-block
   confirmatory study, retaining every post-delivery terminal failure.
5. Complete live observer/broker ablations, audit calibration, cross-system
   cut-set transfer, effect sizes, multiplicity-adjusted uncertainty, and
   safety--recovery--latency analysis.
6. Reproduce the final artifact on an independent machine, generate all tables
   and figures from immutable records, resolve eight result tokens and 35 table
   cells, complete the 15 release items, sanitize the anonymous archive, and
   convert to the selected venue template.

After these conditions are met, rerun the full reviewer audit before any arXiv
upload or peer-review submission. Until then, the allowed description is:
**pre-results protocol plus simulator and controller-contract artifact**.
