# Iteration 12: Agent-C action-binding milestone review

Timestamp: 2026-09-28T23:32:42Z

## Research question

Does iteration 10's complete-tuple gap generalize across the released Agent-C
write-policy corpus, or is it an isolated address-rule artifact?

## Competing explanations

- H1: most released write policies bind every effect-bearing argument to the
  explicit confirmation event; the address rule is an outlier.
- H2: the policies constrain many arguments for local validity but generally
  bind only an identity to confirmation, leaving multiple policy-valid values
  indistinguishable after approval.
- H3: the static classification is a regex artifact and fails known positive
  or negative controls.
- H4: same-identity substitutions fail dynamically once the complete released
  formula and state predicates are applied.

## Smallest discriminating action

Parse all tool methods marked `ToolType.WRITE` in the three released domains,
match each parameter against its target-event patterns, and classify whether
it is a wildcard, recurs elsewhere in the formula, or is explicitly equated to
`action_confirmed.action_id`. Validate the syntactic audit with known controls,
then replay one same-identity value substitution per domain: a second allowed
retail cancellation reason, a second state-eligible airline certificate
amount, and an alternative telecom suspension reason. Pair each with a valid
baseline and an identity-substitution negative control.

## Acceptance and falsification criteria

- The archive must retain published MD5
  `e37f84c00035d7d254170e474e938424`.
- Every released write tool must map to exactly one released specification and
  all selected policies must compile semantically with source-derived schemas.
- Static sanity controls must identify airline cancellation as a complete
  single-argument confirmation tuple, retail order ID as confirmation-bound,
  retail address as wildcard/not confirmation-bound, airline certificate user
  but not amount as confirmation-bound, and telecom suspension reason as a
  wildcard with no confirmation-bound field.
- Each dynamic baseline must be admitted and each identity negative control
  denied before its value-substitution result is interpreted.
- H1 is unsupported if complete confirmation tuples are uncommon across the
  enumerated write corpus. H4 is unsupported if all three locally valid value
  changes remain admissible.
- Syntactic equality is not labeled semantic user authorization, and dynamic
  replay is not labeled an end-to-end attack rate.

## Exact artifacts and configuration

- Agent-C Zenodo archive and CPU-minimal environment: iterations 9–10; archive
  MD5 `e37f84c00035d7d254170e474e938424`; minimal freeze SHA-256
  `eb310ac7c5c100a03f72b5fc1d521fb1baeba8841372ee545d4f44e4eb2c4222`.
- Audit/replay runner: `scripts/audit_agent_c_action_binding.py`, SHA-256
  `6b8abff0daf035dfd8096314ed7473e948821c226ee27a84433305bba1e2092b`.
- Accepted raw report:
  `_workloads/reproduction/iteration-12-agent-c-audit-v2/report.json`,
  SHA-256
  `88ae6f0592d24f00529cc98225e3507edba5e6df373e4b8c523f29f241ea7e51`.
- Preserved first successful audit:
  `_workloads/reproduction/iteration-12-agent-c-audit-v1/report.json`.
- Host/interpreter: Darwin arm64, CPython 3.12.7; released Lark/Z3 checker
  under the documented CPU-minimal substitution; no LLM or domain tool was
  executed.

## Results

The complete released inventory contains 19 write policies and 67 write-tool
arguments:

| Domain | Write policies | Arguments | Confirmation-bound arguments | Complete confirmation tuples | Policies with any wildcard |
|---|---:|---:|---:|---:|---:|
| Retail | 7 | 29 | 7 | 0 | 7 |
| Airline | 6 | 24 | 6 | 1 | 4 |
| Telecom | 6 | 14 | 0 | 0 | 1 |
| **Total** | **19** | **67** | **13** | **1** | **12** |

Only 13/67 arguments (19.4%) are syntactically equated to the explicit
confirmation identifier, and only airline `cancel_reservation` has every
argument bound that way (1/19 policies, 5.3%). Forty arguments have a wildcard
in at least one target-event pattern, spanning 12/19 policies. In contrast,
51/67 arguments recur in some policy predicate. This contrast is important:
local validity constraints are common, but they are not the same property as
binding the approved value.

All eight static sanity checks passed. The three dynamic triples also matched
their expected controls:

- retail `cancel_pending_order`: baseline admitted, alternate allowed reason
  admitted, substituted order denied;
- airline `send_certificate`: baseline amount admitted, another state-eligible
  amount admitted, substituted user denied;
- telecom `suspend_line`: baseline reason admitted, substituted reason
  admitted, substituted customer denied.

Thus all three same-identity value changes were admissible while all three
identity controls were denied.

## Deviations

The accepted v2 run adds domain-level summaries and eight explicit static
sanity controls to the first successful audit. Both runs are preserved. The
released checker's import again emitted its built-in NLTK WordNet update check;
the corpus was already present.

The planned phrase “authority-bearing parameters” was narrowed operationally
to all parameters of methods explicitly marked `ToolType.WRITE`. The audit
does not claim that every write parameter requires direct user confirmation;
some are intentionally derived or policy-constrained.

## Limitations

The static audit recognizes direct syntactic equality between a target-event
variable and `action_confirmed.action_id`. It is not a full dataflow or theorem
prover. A variable recurring elsewhere means only that some formula constrains
it; the constraint may derive from authenticated state, prior tool output, or
an unrelated predicate, and does not prove trusted user intent.

Agent-C's `action_confirmed` event may represent a user's approval of details
shown in natural language even though those details are absent from its formal
event schema. The finding is therefore that the released checker cannot
machine-verify those values against the approval—not that every admitted
alternative is necessarily an exploit in the authors' end-to-end setup.

The three dynamic probes directly supply state predicates and execute no
domain tools or LLM. They establish formula admissibility, not attack
likelihood, completed harm, benign-task success, or published Agent-C metrics.
The corpus belongs to one artifact and three related tau2 domains; external
validity remains limited.

## Interpretation

H1, H3, and H4 are unsupported; H2 is supported at the released-formula level.
The address result is not isolated. Across retail, airline, and telecom,
Agent-C strongly expresses ordering, identity lookup, state validity, and some
resource equality, yet its explicit confirmation representation normally does
not contain the complete value-bearing action tuple.

This does not make temporal conformance obsolete. It defines the compositional
boundary: Agent-C can enforce *when* a valid action may occur and bind selected
identities; SENTINEL's candidate layer binds *which exact normalized values*
were authenticated. The testing-strategy controls prevent treating the
always-deny outcome, a schema-valid call, or an identity-only denial as
equivalent evidence.

## Publication impact

The milestone upgrades complete authenticated action-tuple binding from a
single-policy counterexample to a corpus-wide syntactic gap supported by three
domain-stratified model-free replays. This is credible motivation for a
mechanisms paper, but not yet a publishable efficacy result. Required next
evidence includes matched end-to-end tasks, realistic envelope construction,
multiple benign amendments/ranges, executed effects, and comparison with IFC
and pre/postcondition systems.

The defensible claim is narrow: **released temporal policies can validate
ordering and local state while lacking a machine-checkable representation of
the complete user-approved action tuple**. The paper must not claim that
Agent-C promises full tuple authorization or that 18/19 policies are unsafe.

## Decision

**Continue and pivot to the next defense family.** The Agent-C milestone has
enough evidence to retain complete authenticated tuple binding as a candidate
contribution. Iteration 13 should execute and characterize the pinned Fides
tutorial artifact exactly where possible, freeze its actual enforceable
properties, and distinguish tutorial execution from any later AgentDojo
reconstruction.
