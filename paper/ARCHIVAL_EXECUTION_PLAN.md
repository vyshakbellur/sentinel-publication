# SENTINEL Archival Publication Execution Plan

**Purpose:** convert the development study into a defensible archival evaluation without overstating synthetic evidence.  
**Primary target:** a dependable-systems or software-reliability venue such as DSN or ISSRE; use an IEEE security/workshop paper only for a deliberately narrower mechanism result.  
**Current decision:** do not run the existing live controller as the confirmatory experiment until the protocol-repair gate below passes.

## 1. Archival claim

The archival paper should test this bounded claim:

> An effect-grounded, deterministic boundary can expose and contain classes of
> cross-layer assurance failure that are invisible to policy-verdict and
> tool-receipt metrics, while preserving useful recovery under declared
> workflow and authority constraints.

This is not a claim that deterministic guardrails solve prompt injection, that
SENTINEL is universally superior to information-flow control, or that a
successful receipt proves a safe effect. The confirmatory study must be capable
of rejecting the claim through unsafe effects, unavailable recovery, excessive
refusal, unrepeatable results, or failure of the causal evidence chain.

## 2. Protocol-v2 validity repair

Before collecting confirmatory data, bind each trial to one causal chain:

\[
\text{frozen proposal}\rightarrow\text{canonical action}\rightarrow
\text{policy verdict}\rightarrow\text{broker request}\rightarrow
\text{authenticated effect}\rightarrow\text{application outcome}.
\]

Every eligible terminal record must contain or reference immutable digests for:

- incident template, load seed, deployment block, cluster UID, and namespace;
- raw model response, parsed proposal, model identifier, generation settings,
  prompt, tool catalog, and context;
- canonical action, service-contract revision, adapter, trusted bindings,
  policy bundle, dependency graph, and conflict graph;
- broker request, credentialed actuator identity, semantic effect identifier,
  attempt identifier, idempotency key, and compensation identifier;
- API audit slice, pre/post resource state, application-semantic effect, health
  outcome, and observer signature;
- phase and partition membership, randomization commitment, code revision,
  dependency lock, and analysis revision.

The controller must execute the frozen proposal artifact, not reconstruct a
static equivalent. Digest drift, missing or extra audit effects, an ambiguous
cluster identity, an unsigned observer result, or phase leakage makes the
trial **ineligible**, not safe. Eligibility rules freeze before outcome review.

### Independent evidence channels

Use three evidence channels with separate credentials and failure domains:

1. **API audit:** API-server or service-gateway record of the authenticated
   principal, target, operation, correlation identifier, response, and time.
2. **Resource-state observer:** read-only observation of the actual resource
   before and after execution.
3. **Application-effect observer:** workload-level semantic evidence such as a
   processed order, duplicate charge surrogate, queue item, or SLO recovery.

The actuator may emit receipts but may not grade itself. At least one observer
must run outside the Guardian process and sign the evidence envelope. Exact
reconciliation over a bounded trial window is mandatory: missing and surplus
effects both fail the evidence gate.

## 3. Systems, actions, and baselines

### 3.1 Primary systems

Use two independently resettable systems for confirmation and reserve a third
for transfer or independent reproduction:

| Role | Public system | Frozen revision | Required use |
|---|---|---|---|
| Primary A | Google Online Boutique | `38e7348eb289eb5b87c0c6e8cb19ced0449dc389` | Multi-service incidents, workload recovery, workflow execution |
| Primary B | OpenTelemetry Astronomy Shop | `898ede2f314b2c1e92a2d9a6ebd7efc188709290` and Helm `opentelemetry-demo-0.42.0` | Independent topology and telemetry stack |
| Transfer/replication | Train Ticket | `313886e99befb94be6cd45f085c98e0019f59829` | Optional third-system transfer or reproducer-owned study |

Pin container images by digest, store deployment manifests, and record cluster
and controller versions. A nominal reset test must demonstrate the same clean
state and workload envelope before every block.

### 3.2 Action and workflow vocabulary

The current `set_replicas` action is necessary but insufficient because it is
state-convergent and hides several duplicate-effect failures. Add:

- one idempotent state-setting action, such as replica or feature-state change;
- one non-idempotent semantic action implemented with a safe surrogate, such
  as create-job, enqueue-request, or append-ledger-entry;
- an inspect-then-act sequential dependency;
- a parallel fan-out followed by an authenticated fan-in;
- a conflict pair that must serialize despite agent-declared independence;
- bounded retry, quarantine, rollback, and compensation paths.

Every action receives a canonical effect class, reversibility class, blast
radius, resource identity, tenant, precondition, postcondition, retry policy,
and compensation rule derived outside the model.

### 3.3 Baselines

Implement these conditions over identical frozen proposals:

1. no external boundary;
2. schema validation plus static allowlist;
3. OPA/Rego policy-only reference monitor;
4. Guardian trusted binding plus deterministic policy;
5. Guardian full workflow/effect boundary;
6. always deny as a utility floor.

An information-flow baseline is included only if its labels and trusted inputs
are specified independently. A conceptual reconstruction must be named as such
and must never be presented as the official Fides implementation.

## 4. Executable partitions and holdouts

Freeze executable objects rather than scenario names. Use three disjoint,
content-addressed partitions:

- **development:** implementation, debugging, mechanism discovery, and figure
  design;
- **blinded pilot:** timing, restoration reliability, missingness, dependence,
  and power parameters only; no primary hypothesis tests;
- **confirmatory holdout:** byte-frozen incidents, prompts, model settings,
  mutations, policies, manifests, oracles, exclusions, and analysis code.

Prefer a custodian or external collaborator to create or escrow the holdout.
At minimum, commit its Merkle root or file-digest manifest before the pilot is
unblinded. The controller verifies membership and refuses a case assigned to a
different partition. Development, pilot, census, and confirmation run IDs may
not overlap.

## 5. Repeated probabilistic and infrastructure blocks

Separate proposal generation from paired guardrail replay:

1. generate a proposal once for each planner/model seed and freeze the raw and
   parsed artifacts;
2. replay that identical proposal across every guardrail condition;
3. realize each condition on a freshly restored deployment/load block;
4. independently reconcile audit, resource, and application outcomes.

A block is not repeated API calls against unchanged state. It is a fresh
combination of deployment restoration, incident instance, load seed, proposal
seed, and model seed. Use at least two model families where the action schema
is supported, deterministic ARIA, an oracle proposal, and a deliberately wrong
proposal control.

For the blinded pilot, use the nominal condition plus all single-fault rows,
five guardrails, two systems, and at least six independent blocks:

\[
12\;\text{rows}\times5\;\text{guardrails}\times2\;\text{systems}
\times B,\quad B\ge6.
\]

The final repetition count is selected by simulation-based power using pilot
variance, within-block correlation, restoration failures, and a predeclared
minimum practically important risk difference. Do not choose it from observed
confirmatory outcomes.

## 6. Experimental phases and hard gates

| Phase | Work | Exit gate |
|---|---|---|
| A. Protocol repair | Proposal-to-effect digest binding, authenticated observers, fail-closed eligibility | Twenty consecutive eligible nominal and denial trials per system with exact reconciliation |
| B. Workflow slice | Sequential, parallel, conflict, retry, quarantine, compensation, and non-idempotent surrogate | Every metamorphic workflow oracle passes in clean conditions |
| C. Blinded pilot | Repeated infrastructure/model blocks without primary comparisons | Missingness, timing, correlation, restoration, and power model frozen while labels remain masked |
| D. Fault-surface census | Nominal, 11 singles, and 46 cross-layer pairs once per system/guardrail | Complete 580-cell schedule or transparent predeclared missingness report |
| E. Confirmatory study | Nominal, 11 singles, and seven preregistered mechanism pairs | Complete `190R` eligible cells, where `R` is fixed by the pilot |
| F. Mechanism ablations | Binding, fail-closed handling, observer, idempotency, and compensation | Predicted sensitivity controls observed without contaminating primary estimates |
| G. Independent reproduction | Clean environment, separate operator, immutable artifact | Reproducer regenerates primary tables and reaches predeclared directional agreement |
| H. Submission freeze | Regenerate paper from terminal records | Artifact checker, claim audit, authorship review, and venue checklist pass |

No phase advances merely because the system produced enough JSON. A failed gate
causes repair and a new versioned protocol; it does not permit outcome-dependent
exclusion or silent rerunning.

## 7. Idempotency and compensation experiment

Run a dedicated factorial on the non-idempotent surrogate:

- idempotency: absent, process-local cache, durable effect ledger;
- compensation: absent, best-effort, verified and idempotent;
- fault: none, lost response after effect, duplicate dispatch, delayed response,
  partial fan-out failure;
- guardrail: at least Guardian full and the strongest external baseline;
- repeated independent block: at least six.

This yields `3 × 3 × 5 × 2 × 6 = 540` planned cells before any optional system
replication. Primary outcomes are duplicate semantic-effect rate, uncompensated
effect rate, incorrect compensation rate, safe recovery, and recovery latency.
Treat detection after a duplicate as a security failure even when the observer
raises an accurate alarm.

## 8. Analysis and uncertainty

### 8.1 Primary outcomes

- unauthorized-effect rate;
- safe-recovery rate;
- false-intervention rate;
- duplicate semantic-effect rate;
- uncompensated-effect rate;
- end-to-end recovery time.

Always report raw numerators and denominators. Preserve policy verdict, broker
receipt, authenticated effect, safety judgment, and recovery judgment as
separate columns.

### 8.2 Primary comparisons

Use paired risk differences because conditions receive the same frozen
proposal. Report paired discordant counts and McNemar intervals/tests for the
predeclared headline comparisons. Fit a hierarchical logistic model or
cluster-aware GEE with deployment/incident/proposal blocks and system effects.
Use exact or Bayesian sensitivity analysis if complete separation occurs.

For latency and recovery, use cluster bootstrap intervals. Estimate pairwise
fault interaction on the additive risk scale. Apply Holm correction only to
the preregistered primary family; label all other comparisons exploratory.
For zero observed unsafe effects, report a finite-sample upper bound rather
than zero risk.

### 8.3 Power and robustness

Use simulation rather than an independent-binomial formula. Simulate the exact
paired blocked schedule, pilot-estimated base rates, intraclass correlation,
missingness, and the smallest risk difference worth detecting. Publish the
simulation script and sensitivity curves. Repeat the headline analysis with:

- all eligible records;
- strict complete blocks only;
- exact tests;
- hierarchical estimates;
- worst-case treatment of operationally missing outcomes.

## 9. Independent reproduction

Recruit a reproducer who did not implement Guardian or select the holdout. Give
them only the archived package and a clean-machine procedure. They must:

1. verify source, image, dataset, and holdout digests;
2. provision at least one primary system without author intervention;
3. execute a nominal, denied, single-fault, compound-fault, and
   idempotency/compensation slice;
4. regenerate all primary tables from terminal records;
5. document deviations, failed instructions, and operator time.

Success is not exact equality of stochastic rates. Predeclare acceptable
reproduction as exact deterministic-oracle agreement, verified evidence-chain
integrity, and directional agreement for primary paired effects with all
deviations reported. Archive the reproducer's environment manifest and report
as first-class artifacts.

## 10. Artifact and paper production

The public artifact should contain sanitized code, protocol, frozen manifests,
container/image digests, schemas, terminal records, analysis scripts, and a
one-command deterministic figure/table build. Secrets, cluster credentials,
and unsafe live targets remain excluded. Each paper number must be traceable to
a terminal-record query, and the checker must fail on unmatched values.

Paper structure after confirmation:

1. problem and bounded contribution;
2. relationship to runtime assurance, agent enforcement, and dependable
   workflows;
3. threat model and causal evidence chain;
4. SENTINEL methodology and reference implementation;
5. preregistered systems, partitions, baselines, and analysis;
6. effect-grounded results with uncertainty;
7. mechanism and idempotency/compensation ablations;
8. independent reproduction;
9. threats, limitations, ethics, and negative results.

## 11. Schedule and resourcing

An accelerated but credible path is approximately nine weeks once compute and
operators are available:

| Week | Deliverable |
|---|---|
| 1 | Protocol-v2 schema, digest binding, observer trust split |
| 2 | Two-system nominal/denial calibration and reset validation |
| 3 | Composite workflow plus non-idempotent surrogate |
| 4 | Blinded pilot and frozen power analysis |
| 5 | Fault-surface census |
| 6 | Confirmatory blocks |
| 7 | Idempotency/compensation ablations and sensitivity reruns |
| 8 | Independent reproduction and artifact repairs |
| 9 | Final statistics, paper regeneration, internal review, and submission freeze |

Minimum roles are an experiment owner, a boundary/adapter owner, an
infrastructure operator, a statistics reviewer, and an independent reproducer.
The experiment owner must not unblind and alter the analysis alone.

## 12. Go/no-go rules

Proceed to archival submission only when:

- the frozen proposal demonstrably controls the realized broker request;
- every analyzed live effect is reconciled across authenticated audit and an
  independent application observer;
- at least two systems pass reset and nominal calibration;
- executable holdouts and analysis are frozen before confirmation;
- repeated probabilistic and infrastructure blocks support uncertainty bounds;
- idempotency and compensation mechanisms have controlled ablations;
- a separate operator reproduces the evidence chain and primary tables;
- negative, null, and utility results remain in the manuscript.

If SENTINEL does not outperform a correct external boundary, the paper remains
publishable as a negative result if it demonstrates that common verdict/receipt
evaluations overstate assurance, identifies reproducible cross-layer cut sets,
and releases a rigorous effect-grounded evaluation protocol.
