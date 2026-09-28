# Iteration 01: freeze artifact identities and reproduction classes

Date: 2026-09-28

## Research question

Which core baselines have sufficient public artifacts for exact reproduction,
and which require replication or clean-room reconstruction?

## Competing explanations

- H1: the central deterministic defenses are all directly reproducible from
  public artifacts.
- H2: artifact completeness differs enough that treating all comparisons as
  reproduction would be scientifically misleading.

## Smallest discriminating action

Resolve current repository heads, shallow-inspect AgentDojo, CaMeL, Fides, and
Agent-C, and inspect the Agent-C Zenodo record and archive checksum. Check the
paper records for public ToolGate and Invitation artifacts.

## Acceptance and falsification criteria

- Accept exact-candidate status only when executable code, required dataset or
  environment, and a documented experiment entry point are available.
- Downgrade to artifact replication when infrastructure/models must change.
- Downgrade to conceptual reconstruction when only a paper/tutorial or closed
  changed product is available.
- H1 is falsified if any central comparison lacks a complete experiment
  artifact.

## Configuration and evidence

Resolved sources and revisions are recorded in
`external/research_artifacts.lock.json`. Temporary inspection clones were kept
outside the repository and were not vendored. The Agent-C Zenodo archive was
66,633,222 bytes and matched `md5:e37f84c00035d7d254170e474e938424`.

## Results

- AgentDojo and CaMeL expose runnable experiment entry points and are exact
  reproduction candidates, subject to model/API availability.
- Agent-C's GitHub repository is only a placeholder, but its Zenodo artifact is
  complete and contains tau2 data, domain specifications, baseline wrappers,
  evaluation commands, and utilities.
- Fides provides an executable tutorial notebook but not the paper's complete
  AgentDojo evaluation pipeline.
- ToolGate's arXiv/ACL record exposes the paper but no implementation link was
  found in this audit.
- Invitation evaluates a closed product whose behavior has changed since
  disclosure; its causal scenarios can be reconstructed but its reported
  product behavior cannot be exactly reproduced.

## Deviations and limitations

This iteration audited availability, not executability. Repository `HEAD` is a
time-of-audit identifier, not necessarily the authors' paper tag. Licenses,
dependency solvability, API/model availability, and scorer recovery remain for
iteration 2 and 3. Absence of a ToolGate link in the inspected records does not
prove that no author artifact exists elsewhere.

## Interpretation and publication impact

H1 is falsified and H2 is supported. The study must carry an evidence-class
field through every result. This increases credibility and makes partial
reproducibility itself reportable. It also means SENTINEL must not claim wins
against paper-only reimplementations as if they were author implementations.

## Decision

**Continue.** Build isolated environments, audit licenses and dependencies, and
identify the smallest no-cost reproducible smoke experiments. No experiment is
currently running, so no delayed status check is needed.

