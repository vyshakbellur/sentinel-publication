# Iteration 17: common append-only action/effect trace interface

Timestamp: 2026-09-29T00:53:08Z

## Research question

Can CaMeL, Agent-C, the Fides reconstruction, ToolGate, no-defense, and
always-deny evidence be represented in one action/effect trace without changing
native metrics, inventing missing execution evidence, or conflating verdicts,
dispatches, receipts, and effects?

## Competing explanations

- H1: a common interface necessarily renames or reinterprets native metrics.
- H2: missing dispatch, receipt, or effect evidence will be silently coerced to
  false and create spurious agreement.
- H3: an append-only event model can preserve native objects exactly while
  adding explicitly sourced stages and field-to-field comparisons in a separate
  namespace.
- H4: the interface cannot express both agreement and disagreement across the
  selected baselines and controls.
- H5: record or event tampering cannot be detected deterministically.

## Smallest discriminating action

Implement an immutable action/effect trace with hash-chained events, explicit
`observed`, `not_observed`, and `not_applicable` statuses, an opaque native
namespace, and comparisons that name exact boolean fields. Freeze six selected
records before normalization: one CaMeL resource substitution, one Agent-C
formula replay, one Fides adapter-mislabel row, one ToolGate false-success row,
and the paired ToolGate-harness no-defense and always-deny controls. Verify
source hashes, native-object round trips, event chains, expected comparisons,
and negative invariants.

## Acceptance and falsification criteria

- All six source selections must retain exact native object equality after
  normalization.
- All six event chains must validate and a changed previous-event digest must
  fail validation.
- Unobserved events must reject nonempty payloads.
- Missing effect evidence must produce `not_computable`, never `agree` or
  `disagree` through false imputation.
- The 12 preregistered comparisons must yield six agreements, four
  disagreements, and two not-computable results.
- Required spot checks must include CaMeL trusted-authority/effect disagreement,
  Agent-C not-computability, Fides agreement, ToolGate false-success
  disagreement, and always-deny agreement.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/action_effect_trace_validation.json`,
  SHA-256
  `d5ada0283e1e0857d6ede1243b5321fefaee494af63d0f605e2f83e9acb9a59b`.
- Interface implementation:
  `sentinel_experiments/action_effect_trace.py`, SHA-256
  `e05ed43bea1e2aacb5dac0a035a2204692185992b9aa6bc4115203ec9adebd3e`.
- Baseline normalization runner:
  `scripts/normalize_baseline_action_effect_traces.py`, SHA-256
  `5173cb829962cbca1cbe9bc62b30560ae0446fa6ec4e461f2c8fa2a42e6c471e`.
- Focused tests: `tests/test_action_effect_trace.py`, SHA-256
  `6f477e2af82d2bd0b0870db522286cee17d9e99012a4e03053693e27e7b472f4`.
- Design document: `docs/ACTION_EFFECT_TRACE_INTERFACE.md`, SHA-256
  `f48d36fa62cc897454bd45f5c5ec4237213b880132275dadfa6286c791312f5c`.
- Accepted raw report:
  `_workloads/reproduction/iteration-17-action-effect-trace-v1/report.json`,
  SHA-256
  `3bc5e9b2899f9ef13b826af8ae854a20811514a35e7907c88e94df212350248d`.
- Input revisions and report hashes are inherited unchanged from iterations 8,
  12, 14, and 15 and are pinned in the protocol.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network, service, or
  external effect was invoked.

## Results

The accepted report contains six traces. All six hash chains validated and all
six `native_namespace` objects are exactly equal to their selected source
objects. The 12 explicit comparisons matched the preregistration:

| Status | Count |
|---|---:|
| Agree | 6 |
| Disagree | 4 |
| Not computable | 2 |

The selected comparisons demonstrate the intended separation:

- **CaMeL:** the native allow verdict agrees with the completed effect, while
  the independently preregistered trusted-authority expectation disagrees with
  it (`false` authorization versus `true` effect).
- **Agent-C:** formula admission is observed, but dispatch, receipt, and effect
  are explicitly not observed; native-verdict/effect comparison is therefore
  not computable.
- **Fides reconstruction:** native AgentDojo attack achievement, dispatch, and
  the independent exact-write indicator agree under the mislabeled adapter.
- **ToolGate false success:** symbolic acceptance/commit, dispatch, and a valid
  receipt each disagree with the absent independent effect.
- **No defense:** there is no native guardrail verdict, so verdict/effect is not
  applicable/not computable; dispatch and effect agree.
- **Always deny:** the negative native verdict, absent dispatch, and absent
  effect agree without being credited as utility.

Five focused tests passed, including negative tests for payload on an unobserved
event and a tampered digest chain. A fresh normalization run reproduced the
accepted report byte-for-byte.

## Deviations

The interface is implemented as frozen Python data contracts rather than a
standalone JSON Schema. This permits executable invariants over digest chains
and missingness in this iteration; a serialization schema can be generated or
added before external artifact release.

The optional `ruff` executable was unavailable in the current shell, so that
lint command failed before checking files. A direct 88-column scan found and
fixed the two long lines, `py_compile` passed, and the focused and full test
suites provide the recorded verification.

The baseline adapters are deliberately report-specific. They do not modify or
vendor any third-party source.

## Limitations

Only six development records are normalized, one per selected baseline
condition plus controls. Exact native round-trip equality prevents field loss
but does not prove that every adapter semantic description is correct. The
source studies remain heterogeneous, so a common container does not make their
effect sizes directly comparable.

Version 1 represents a single logical action and boolean equality comparisons.
It lacks workflow/action parent IDs, concurrent causality, attempt numbers,
observer identity, observation windows, signatures, trusted timestamps, and a
relation registry. SHA-256 chaining detects changed serialized events under the
stored record; it is not a signed or externally anchored audit log.

The Fides record remains a conceptual reconstruction. Agent-C's missing domain
effect correctly prevents a comparison but also limits the currently usable
cross-baseline matrix. No security or efficacy outcome is newly estimated by
this interface-validation iteration.

## Interpretation

H1, H2, H4, and H5 are rejected; H3 is supported for the selected records. A
common trace can preserve native semantics and still expose cross-layer
relations, provided missingness is first-class and derived comparisons remain
outside native namespaces.

The result sharpens the independent-effect claim. ToolGate's false-success row
has three different upstream positives—native symbolic commit, dispatch, and
receipt—but an absent effect. Agent-C's formula result cannot be treated the
same way because execution is absent from its evidence. The interface prevents
these two cases from being pooled incorrectly.

## Publication impact

This supplies the minimum reproducible evidence substrate required for a
credible assurance-evaluation paper. It directly addresses a common review
risk: silently converting incomparable baseline outcomes into one metric. It
does not itself establish novelty or effectiveness, but it makes later matched
oracle, substitution, and cut-set experiments auditable.

The system-design skill materially influenced the separation of components,
data flow, missingness semantics, append-only integrity, trade-offs, and the
explicit list of fields to add for multi-action workflows.

## Decision

**Continue.** Iteration 18 should add independent environment-effect oracle
records and disagreement metrics over multiple controlled failure modes using
this interface. It must retain the original native namespaces, include
no-defense and always-deny controls, and show whether effect observation changes
the scientific conclusion beyond the already selected ToolGate fixture.
