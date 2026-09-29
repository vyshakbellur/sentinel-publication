# Common action/effect trace interface

Status: development interface validated in reproduction-campaign iteration 17.

## Purpose and constraints

The interface permits cross-baseline assurance analysis without translating a
baseline's native success, utility, attack, or conformance metric into a new
meaning. It must:

- preserve the selected native object exactly in `native_namespace`;
- represent missing evidence explicitly as `not_observed`, never as `false`;
- separate proposal, normalized action, binding, verdict, dispatch, receipt,
  effect, and state observations;
- keep derived SENTINEL comparisons outside native metrics;
- make every comparison name the two exact boolean fields it relates; and
- expose tampering or reordering through an append-only digest chain.

This is an evidence interchange record, not a new policy language, workflow
engine, broker protocol, or claim that all baseline metrics are comparable.

## Data flow

```text
pinned native report
        |
        +---- exact selected object ----------> native_namespace
        |
        +---- baseline-specific adapter ------> hash-chained events
                                                  |
                         proposal -> action -> binding -> native verdict
                                                  |
                                      dispatch -> receipt -> effect -> state
                                                  |
                              explicit field-to-field comparisons
```

Each adapter is intentionally small and evidence-losing transformations are
forbidden. If a source records formula admission but no domain-tool execution,
the dispatch, receipt, and effect events are `not_observed`; they are not
manufactured from the admission result.

## Record model

An `ActionEffectTrace` header contains:

- trace and baseline identity;
- evidence class and source-report SHA-256;
- the exact native object and its canonical digest;
- injected fault identifiers; and
- an ordered tuple of `TraceEvent` records.

Every event contains a contiguous sequence, stable event ID, stage, observation
status, source namespace, semantic description, JSON payload, previous-event
digest, and its own digest. `not_observed` and `not_applicable` events must have
an empty payload.

Comparisons are separate records with a comparison ID, left and right event
IDs, left and right field names, relation, source values, and one of `agree`,
`disagree`, or `not_computable`. Version 1 permits only explicit boolean
equality. This restriction prevents an adapter from silently equating, for
example, Agent-C formula admission with a completed external effect.

## Validated baseline mappings

| Baseline | Native evidence preserved | Last independently supported stage |
|---|---|---|
| CaMeL probe | Complete selected observation row | Environment mutation effect |
| Agent-C replay | Complete selected dynamic replay object | Native formula verdict; execution is not observed |
| Fides reconstruction | Complete selected AgentDojo row | Exact attack-write execution indicator |
| ToolGate probe | Complete selected scenario row | Independent in-memory effect sink |
| No defense / always deny | Complete ToolGate control rows | Independent in-memory effect sink |

The iteration-17 validation includes six traces, all with valid chains and exact
native round trips. It deliberately produces both computable disagreements and
`not_computable` outcomes.

## Assumptions and trade-offs

- One trace currently describes one selected logical action. Multi-action and
  parallel workflows will need action IDs and causal-parent IDs on every event.
- Canonical JSON and SHA-256 provide reproducible integrity evidence, not a
  signature, trusted timestamp, or durable append-only store.
- Adapter semantic descriptions remain reviewable human text. Future versions
  should use a registry of comparison relations without removing the text.
- Exact native preservation increases record size but prevents metric drift and
  makes an adapter audit possible.
- Explicit missingness reduces the number of comparable rows, which is the
  scientifically correct alternative to imputing an effect from a verdict.

## What to revisit as the study grows

Before multi-service, concurrent, or confirmatory evaluation, add workflow and
action identifiers, causal parents, attempt numbers, observer identity,
observation windows, signed source references, and state/effect tuple schemas.
Version migration must be additive or provide a checked converter; existing
native namespaces and event digests must never be rewritten in place.
