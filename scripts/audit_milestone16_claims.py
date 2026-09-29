"""Falsify broad SENTINEL novelty claims against pinned baseline evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_verified(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = root / spec["path"]
    actual = _digest(path)
    if actual != spec["sha256"]:
        raise SystemExit(
            f"evidence hash mismatch for {path}: expected {spec['sha256']}, got {actual}"
        )
    return json.loads(path.read_text())


def main() -> int:
    args = _args()
    root = args.repository.resolve()
    protocol_path = args.protocol.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing evidence: {output}")
    protocol = json.loads(protocol_path.read_text())
    evidence = {
        name: _load_verified(root, spec)
        for name, spec in protocol["source_reports"].items()
    }

    agent_c = evidence["agent_c"]
    admitted_value_substitutions = sum(
        values[key]
        for values in agent_c["dynamic_replays"].values()
        for key in values
        if key in {
            "alternate_allowed_reason",
            "substituted_eligible_amount",
            "substituted_reason",
        }
    )
    toolgate_substitution = next(
        row
        for row in evidence["toolgate"]["rows"]
        if row["scenario"] == "toolgate_substitution"
    )
    extracted = {
        "agentdojo_native_scorer_disagreements": evidence["agentdojo"][
            "scorer_pair_summary"
        ]["expected_native_scorer_disagreements"],
        "camel_fully_bound_operations": evidence["camel_static"]["summary"][
            "fully_strictly_bound_operation_count"
        ],
        "camel_side_effect_operations": evidence["camel_static"]["summary"][
            "side_effect_operations"
        ],
        "camel_untrusted_resource_effects": evidence["camel_dynamic"]["summary"][
            "untrusted_resource_effects"
        ],
        "agent_c_complete_confirmation_tuples": agent_c[
            "complete_confirmation_tuple_policy_count"
        ],
        "agent_c_write_policies": agent_c["write_policy_count"],
        "agent_c_admitted_same_identity_value_substitutions": admitted_value_substitutions,
        "sentinel_tuple_baseline_utility": evidence["sentinel_tuple"]["summary"][
            "sentinel"
        ]["baseline_utility"],
        "sentinel_tuple_mutations_blocked": evidence["sentinel_tuple"]["summary"][
            "sentinel"
        ]["mutations_blocked"],
        "sentinel_tuple_mutations_total": evidence["sentinel_tuple"]["summary"][
            "sentinel"
        ]["mutations_total"],
        "fides_tutorial_policy_matrix_matches": evidence["fides_tutorial"][
            "policy_matrix_matches"
        ],
        "fides_correct_label_attacks": evidence["fides_reconstruction"]["summary"][
            "fides_correct_label"
        ]["native_attack_goals_achieved"],
        "fides_mislabeled_adapter_attacks": evidence["fides_reconstruction"][
            "summary"
        ]["fides_mislabeled_adapter"]["native_attack_goals_achieved"],
        "toolgate_native_effect_disagreements": evidence["toolgate"]["summary"][
            "native_effect_disagreements"
        ],
        "toolgate_substituted_destination_effect": toolgate_substitution[
            "independent"
        ]["unauthorized_effect"],
    }

    gap_families = []
    if extracted["camel_untrusted_resource_effects"] >= 2:
        gap_families.append("CaMeL")
    if extracted["agent_c_admitted_same_identity_value_substitutions"] >= 2:
        gap_families.append("Agent-C")
    if extracted["toolgate_substituted_destination_effect"]:
        gap_families.append("ToolGate")

    disagreement_contexts = []
    if extracted["agentdojo_native_scorer_disagreements"] >= 1:
        disagreement_contexts.append("AgentDojo native scorer")
    if extracted["toolgate_native_effect_disagreements"] >= 1:
        disagreement_contexts.append("ToolGate symbolic commit")

    rules = protocol["decision_rules"]
    novelty_eliminations = {
        claim: {
            "status": "eliminated_as_novel_mechanism",
            "direct_prior_art_families": families,
        }
        for claim, families in protocol["direct_prior_art"].items()
        if len(families)
        >= rules["eliminate_mechanism_novelty_when_direct_prior_art_families_at_least"]
    }
    attribute_binding_retained = (
        len(gap_families)
        >= rules["retain_attribute_binding_candidate_when_gap_baseline_families_at_least"]
        and extracted["sentinel_tuple_baseline_utility"] == 1
        and extracted["sentinel_tuple_mutations_blocked"]
        == extracted["sentinel_tuple_mutations_total"]
    )
    effect_observation_retained = (
        len(disagreement_contexts)
        >= rules["retain_effect_observation_candidate_when_disagreement_contexts_at_least"]
    )
    candidate_decisions = {
        "trusted_attribute_binding": {
            "status": (
                "retain_as_narrow_empirical_candidate"
                if attribute_binding_retained
                else "drop"
            ),
            "gap_baseline_families": gap_families,
            "novelty_limit": "Policy predicates can express equality; the candidate is trusted complete-tuple construction and evaluation, not tuple predicates themselves.",
        },
        "independent_effect_observation": {
            "status": (
                "retain_as_evaluation_candidate"
                if effect_observation_retained
                else "drop"
            ),
            "disagreement_contexts": disagreement_contexts,
            "novelty_limit": "Application-state assertions are prior art; the candidate is cross-layer verdict/effect disagreement analysis.",
        },
        "non_transitive_resource_transitions": {
            "status": "untested_hypothesis",
            "reason": "No executed URL/file transition experiment exists by milestone 16.",
        },
        "cross_layer_assurance_cut_sets": {
            "status": "motivated_but_untested_claim",
            "reason": "Individual Fides and ToolGate boundary faults exist, but no combined or minimal cut-set experiment has run.",
        },
    }

    missing = protocol["known_missing_publication_evidence"]
    publication_ready = all(missing[item] for item in rules["publication_ready_requires"])
    fidelity = {
        "published_effectiveness_numbers_reproduced": 0,
        "CaMeL": "artifact execution and deterministic policy probes; no published number",
        "Agent-C": "artifact replication with dependency substitutions and model-free replay; no published number",
        "Fides": "tutorial artifact execution plus conceptual AgentDojo reconstruction; no published number",
        "ToolGate": "official artifact mechanism execution; no published number",
    }
    accepted = (
        len(novelty_eliminations) == len(protocol["direct_prior_art"])
        and attribute_binding_retained
        and effect_observation_retained
        and not publication_ready
    )
    report = {
        "schema_version": "sentinel.milestone16-claim-audit.v1",
        "protocol_sha256": _digest(protocol_path),
        "verified_source_hashes": {
            name: spec["sha256"] for name, spec in protocol["source_reports"].items()
        },
        "extracted_evidence": extracted,
        "novelty_eliminations": novelty_eliminations,
        "candidate_decisions": candidate_decisions,
        "baseline_fidelity": fidelity,
        "publication_ready": publication_ready,
        "missing_publication_evidence": [key for key, value in missing.items() if not value],
        "recommended_framing": "cross-layer assurance evaluation with trusted tuple construction and independent effect oracles; retain a replication/negative-results fallback",
        "accepted": accepted,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "accepted": accepted,
                "publication_ready": publication_ready,
                "eliminated_claims": len(novelty_eliminations),
                "candidate_decisions": candidate_decisions,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
