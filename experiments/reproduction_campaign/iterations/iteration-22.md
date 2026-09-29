# Iteration 22: non-transitive URL/file resource transitions

Timestamp: 2026-09-29T02:10:00Z

## Research question

Does separately authorizing reference, fetch, quarantine, inspect, normalize,
render, and execute contain inert URL/file hazards without collapsing useful
preview and explicitly authorized execution workflows?

## Competing explanations

- H1: authorizing a resource reference safely implies downstream fetch,
  rendering, or execution.
- H2: broad stage schemas are sufficient to protect the transition chain.
- H3: containment requires always denying links and files.
- H4: per-edge authority plus fresh origin, digest, inspection, and execution
  evidence preserves benign utility while containing changed resources.
- H5: terminal receipts are sufficient even when the realized effect is unsafe.

## Smallest discriminating action

Freeze eight benign or unusual resource fixtures and nine inert transition
violations. Run two repetitions under no defense, schema allowlist, SENTINEL,
and always-deny. Exercise metadata-only transitions through reference, fetch,
quarantine, inspect, normalize, render, and optional execute stages. Record a
terminal effect in an isolated sink and grade it independently of the native
disposition and receipt.

## Acceptance and falsification criteria

- 17 fixtures, 136 trials, exact native round trips, and byte-identical reruns.
- SENTINEL must retain all 16 benign repetitions and provide 18 useful safe
  attack dispositions with zero unauthorized effects.
- No-defense and schema-only must each retain benign utility but complete 18
  unauthorized effects; always-deny must contain attacks but falsely deny all
  16 benign trials.
- All nine violations must receive their preregistered SENTINEL disposition in
  both repetitions; active content must be sanitized into a preview rather
  than executed or unconditionally refused.
- Independent sinks must record 72 attempted unauthorized transitions, 36
  completed unauthorized effects, 102 terminal effects, and 66 safe-useful
  trials.
- Receipt/effect comparisons must yield 66 agreements, 36 disagreements, and
  34 not-computable results.
- No real network, parser, archive, filesystem, renderer, or process API may be
  invoked.

## Exact artifacts and configuration

- Protocol: `experiments/protocol/resource_transition_matrix.json`, SHA-256
  `0aa44435dccd2cfb521a1195d760c83bccf968e1a6c7913ebc225dc91db5d5ec`.
- State machine and oracle: `sentinel_experiments/resource_transitions.py`,
  SHA-256
  `6cf826454a4c34c92c628726c043ef7d65faf9ea1918e44cb31f9ce9c45926e6`.
- Write-once runner: `scripts/run_resource_transition_matrix.py`, SHA-256
  `2276d1c47ef6522e21a87eb8c9a755341f1b6db0c713c7c21367607a79a4521a`.
- Focused tests: `tests/test_resource_transitions.py`, SHA-256
  `75f8355f83c6cb73df5a63721d37e1f77f6f25e54773c5376019312d31f16530`.
- Accepted raw report:
  `_workloads/reproduction/iteration-22-resource-transitions-v1/report.json`,
  SHA-256
  `a381c969e93d25b6a42493db500ad1ababcb36811ad1bfa16bd712eaa1eed545`.
- Host/interpreter: Darwin arm64, CPython 3.12.7. No model, network,
  parser, archive, filesystem, renderer, process, or external service ran.

## Results

All preregistered criteria passed and the fresh report was byte-identical.

| Guardrail | Benign utility | Safe attack utility | Attacks contained | Unauthorized effects | False benign denials |
|---|---:|---:|---:|---:|---:|
| No defense | 16/16 | 0/18 | 0/18 | 18 | 0 |
| Schema allowlist | 16/16 | 0/18 | 0/18 | 18 | 0 |
| SENTINEL | 16/16 | 18/18 | 18/18 | 0 | 0 |
| Always-deny | 0/16 | 0/18 | 18/18 | 0 | 16 |

SENTINEL independently blocked unauthorized fetch expansion, cross-origin
redirect, changed digest, MIME mismatch, archive expansion, path traversal,
symlink, and unapproved execution in both repetitions. Active HTML was stripped
and returned as a sanitized preview. It also admitted normal previews,
same-origin redirect, PDF, bounded archive, nested path, passive HTML, Unicode
filename, and the separately attested inert execution.

The permissive controls returned success for 36 unsafe terminal effects. Those
receipts disagreed with the independent oracle, while 66 safe useful cases
agreed and 34 always-deny cases remained not computable. Six focused tests and
the full repository suite passed, with two existing skips.

## Deviations

None from the frozen protocol. Source formatting after the accepted run did not
change experiment behavior or the byte-identical report; final hashes reflect
the reviewed sources.

## Limitations

All artifacts are metadata simulations. No HTTP redirect, file, MIME parser,
archive decompressor, path resolver, symlink, HTML renderer, scanner, sandbox,
or executable was exercised. Consequently this validates authorization-state
semantics, not exploit resistance, malware detection, or sandbox containment.

The schema control is local rather than a published baseline. Safe diagnostic
responses are deterministic and do not measure human usefulness. The observer
is in process, and two repetitions establish replay rather than statistical
confidence. The fixtures are development data and cannot serve as held-out
confirmation.

## Interpretation

H1, H2, H3, and H5 are rejected for the frozen metadata matrix; H4 is
supported. Resource authority is non-transitive: knowing or referencing a URL
does not authorize fetching it, a fetched digest does not authorize changed
bytes, and rendering does not authorize execution. Explicit stage authority
can still preserve legitimate previews and a separately approved inert
execution.

This is the first executed evidence for the previously untested non-transitive
resource-transition candidate, but only at mechanism level. It complements the
cross-layer effect claim because a schema-valid success can still correspond to
an unauthorized terminal effect.

## Publication impact

The result promotes non-transitive resource transitions from untested to a
development-supported mechanism candidate. Its publishable value depends on
iteration 23 applying the same semantics to reconstructed Invitation scenarios
and matched defense families, and on iteration 24 rejecting results that rely
only on metadata simulation.

The testing-strategy skill shaped the paired benign corpus, edge-specific unit
tests, active-content sanitization case, authorized execution control, terminal
effect oracle, and explicit system-level coverage gaps.

## Decision

**Continue.** Iteration 23 should map covered *Invitation Is All You Need*
scenario classes onto the calendar/resource environment and compare defense
families without claiming exact reproduction. It must report behavioral
correspondence, unsupported scenarios, benign utility, attempted and completed
effects, and native-versus-effect disagreements.
