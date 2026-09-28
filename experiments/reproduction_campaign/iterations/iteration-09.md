# Iteration 09: Agent-C model-free artifact smoke

Timestamp: 2026-09-28T22:45:44Z

## Research question

Can the pinned Agent-C Zenodo artifact's temporal checker and released
specification grammar execute on the available CPU-only Darwin host under a
clearly documented minimal substitution, and can its logic distinguish a
resource authorized earlier from a substituted resource?

## Competing explanations

- H1: the model-free checker is inseparable from the artifact's Linux/CUDA and
  constrained-generation stack.
- H2: a CPU-native subset can parse the released specifications and enforce a
  temporal resource-equality rule without an LLM.
- H3: Agent-C enforces order but cannot distinguish a resource substitution
  when the action type remains valid.
- H4: the artifact contains an immediately runnable exact environment on this
  host.

## Smallest discriminating action

Re-download the exact Zenodo archive, verify its published checksum, create a
fresh Python 3.12 environment containing only the model-free checker's pinned
CPU-native dependencies, grammar-parse every nonempty released retail,
airline, and telecom specification, and run one synthetic temporal rule. The
rule requires `authorize(resource_id=r2)` before `delete(resource_id=r1)` with
`r2 == r1`; test no authorization, matching authorization, and substituted
resource conditions.

## Acceptance and falsification criteria

- The artifact identity passes only if the 66,633,222-byte archive has MD5
  `e37f84c00035d7d254170e474e938424`.
- H2 requires zero grammar failures among nonempty released specifications and
  the temporal result vector `[deny, allow, deny]` for no authorization,
  matching resource, and substituted resource.
- H3 is rejected only if the different-resource case is denied while the
  matching-resource control is allowed.
- H4 requires the released full requirements to install without platform
  substitutions; the already identified CUDA/NVIDIA constraints falsify it on
  Darwin arm64.
- No native paper result is claimed without a released model-backed tau2 run.

## Exact artifacts and configuration

- Zenodo record: `10.5281/zenodo.21095899`.
- Archive: `agent-c-icse-artifact.zip`, 66,633,222 bytes, MD5
  `e37f84c00035d7d254170e474e938424`, SHA-256
  `71cfd2118549edc95e69c5d0542645b2803353d76388c8169faed03ef1e8c067`.
- Released `requirements.txt` SHA-256:
  `9b6d8c392f1994cc6006d554df07d99ac1a6bd6081083788ed7fff4b957c5378`.
- Host/interpreter: Darwin arm64, CPython 3.12.7.
- Minimal key packages: Lark 1.2.2, Z3 Solver 4.15.3.0, NLTK 3.9.1,
  Gensim 4.3.3, NumPy 1.26.4, and SciPy 1.13.1.
- Full minimal freeze:
  `_workloads/reproduction/iteration-09-agent-c-artifact-v1/minimal-freeze.txt`,
  SHA-256
  `eb310ac7c5c100a03f72b5fc1d521fb1baeba8841372ee545d4f44e4eb2c4222`.
- Runner: `scripts/smoke_agent_c_checker.py`, SHA-256
  `dce1585a4252e228851e8f68737c5a861511b98edc2394ffcbbae2c383b0c0e5`.
- Accepted raw report:
  `_workloads/reproduction/iteration-09-agent-c-checker-v2/report.json`,
  SHA-256
  `f33ba6521ec1bf44b69eddf4966119a8cd7dd778e49131dfdab70a5439d220ef`.
- Preserved first runner report:
  `_workloads/reproduction/iteration-09-agent-c-artifact-v1/report.json`.

## Results

- The downloaded archive matched the published size and MD5 checksum.
- The artifact contains 37 handwritten specifications: 13 retail, 12 airline,
  and 12 telecom. Six are intentionally empty/unconstrained under the released
  checker's `add_spec` semantics; all 31 nonempty specifications passed the
  released grammar parser.
- The CPU-native Z3 checker accepted the synthetic rule as satisfiable.
- Without an authorization event, deleting resource A was denied.
- After authorizing resource A, deleting A was allowed.
- After authorizing resource A, deleting resource B was denied.

This rejects H3 for an explicitly specified equality relation: Agent-C can
bind a temporal authorization to the same resource identity, not merely to the
same action type.

## Deviations

The full frozen environment was not installed. It unconditionally includes
CUDA/NVIDIA packages and Triton, while the model-free path used only CPU-native
checker dependencies and imported the released source directly. Torch,
Transformers, SynCode/IterGen, the tau2 CLI, and all LLMs were omitted.

The first runner attempt passed no runtime tool-type dictionary to the semantic
transformer and failed all typed specifications. The corrected write-once run
uses the underlying released grammar parser for syntax coverage and reserves
semantic execution for an explicit typed synthetic rule. It also recognizes
empty strings as intentionally unconstrained, matching
`AgentCChecker.add_spec`. Both attempts are preserved.

Importing the released checker triggered its built-in NLTK WordNet download to
the user's NLTK data directory; later imports reported the corpus up to date.
This undocumented import-time network side effect is recorded but is not an
efficacy result.

## Limitations

Grammar parsing is not semantic compilation of all 31 rules. The synthetic
rule proves a mechanism capability, not released-domain correctness or paper
performance. No user simulator, tool environment, constrained decoder, local
model, native reward, conformance rate, harm rate, or runtime distribution was
measured. The minimal environment has transitive dependency drift and cannot
be called exact reproduction.

The six empty specifications include tools that may intentionally require no
temporal restriction; their presence is not treated as a defect without a
domain-policy analysis.

## Interpretation

H1, H3, and H4 are rejected; H2 is supported for the model-free substrate.
Agent-C is a stronger overlap baseline than CaMeL for resource binding when a
specification explicitly equates the authorized and executed identifiers.
SENTINEL therefore cannot claim that attribute equality across workflow steps
is novel. The remaining candidate distinction is how complete action tuples
are derived from authenticated intent, how omissions are detected, and whether
the observed external effect still matches the authorized tuple.

## Publication impact

The result narrows the novelty claim early, which improves the paper. Agent-C
must be compared as a temporal/identity-binding baseline, not described as
order-only. Conversely, the need for handwritten complete specifications and
the absence of effect observation remain hypotheses to test, not conclusions.
This iteration establishes artifact access and a working checker substrate but
does not reproduce a paper number.

## Decision

**Continue.** Iteration 10 should semantically compile a small stratified set
of released benign rules with their real tau2 tool schemas and replay
ground-truth-like traces model-free. This is the cheapest valid test of benign
temporal conformance before any local-model substitution.
