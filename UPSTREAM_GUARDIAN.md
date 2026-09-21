# Guardian snapshot provenance

SENTINEL bundles the Guardian reference guardrail so that a paper artifact does
not depend on an unpublished working tree.

- Source repository: `https://github.com/vyshakbellur/guardian-paradigm.git`
- Local source branch: `codex/protocol-neutral-control-plane`
- Source HEAD: `17dca60d4162ff6ce401624de657f20bc974759c`
- Snapshot date: 2026-09-21
- Snapshot content digest: `57fa794e93d39575aed3f5ee295472f0ae65cd036ca0c892b3da1dd63cb01bb8`
- License: MIT; preserved in `THIRD_PARTY_NOTICES/guardian-paradigm-LICENSE`

The source working tree was dirty. In particular, `guardian/control_plane/`,
`guardian/schemas/agent_proposal.json`, and `tests/test_trusted_binder.py` were
untracked, while `guardian/layers/progressive_cost.py` and
`guardian/schemas/canonical_action.json` were modified. The digest above is the
authority for the bundled source, not the Git commit alone.

Excluded from the snapshot: workshop notebooks, generated talk figures,
runtime caches, Redis state, and workshop release tests. One experiment helper
required by the scenario-matrix regression test is retained. The copied
regression tests are in `guardian_tests/`.

To refresh the snapshot, record a clean upstream commit if possible, replace
the copied source, recompute a deterministic file-list digest, run both test
suites, and update this file in the same commit.
