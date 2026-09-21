# ADR 0001: Private SENTINEL research monorepo

- Status: accepted
- Date: 2026-09-21

## Context

SENTINEL evaluates deterministic guardrails around predictive remediation.
Guardian provides the first guardrail implementation and ARIA provides fallible
proposals. The public Guardian checkout contains unpublished control-plane work,
while `guardian-workshop` is intentionally public and pedagogical. A branch in
a public GitHub repository is not private.

The research artifact must reproduce the exact safety boundary used in every
trial, while avoiding duplicated public benchmark histories and preserving the
independent identity of ARIA.

## Decision

SENTINEL is the private research monorepo and system of record for experiments.

1. Bundle a source snapshot of the Guardian implementation and its relevant
   regression tests, with upstream commit, dirty-state disclosure, license, and
   content digest.
2. Keep ARIA separate. Exchange immutable, schema-versioned proposal records;
   never let SENTINEL depend on an online model call during replay.
3. Keep `guardian-workshop` public and separate. It may consume released
   concepts later, but it is not the research artifact.
4. Do not vendor benchmark systems. Pin their URLs and exact commits in a lock
   file, fetch them to an ignored directory, and record container/deployment
   digests in every experiment manifest.
5. Commit source, protocols, schemas, analysis, and curated evidence. Keep raw
   cluster traces in immutable external storage and commit their checksums.

## Consequences

The repository is self-contained for unit and simulator experiments. Live
experiments remain reproducible without bloating history. Guardian fixes made
here must be deliberately upstreamed; snapshot drift is visible rather than
silent. The repo must not be pushed to either existing public remote.

## Rejected alternatives

- A private branch of Guardian: branches in a public repository are public.
- Git submodule at Guardian HEAD: the required control plane is not represented
  by the public commit.
- Copy ARIA and all workloads: obscures component boundaries and creates a
  large, hard-to-audit artifact.
