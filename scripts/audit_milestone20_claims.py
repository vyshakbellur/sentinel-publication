"""Audit milestone-20 claims after subtracting established mechanisms."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_verified(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = root / spec["path"]
    actual = _sha256(path)
    if actual != spec["sha256"]:
        raise SystemExit(
            "evidence hash mismatch for "
            f"{path}: expected {spec['sha256']}, got {actual}"
        )
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repository.resolve()
    protocol_path = args.protocol.resolve()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite evidence: {args.output}")
    protocol = json.loads(protocol_path.read_text())
    evidence = {
        name: _load_verified(root, spec)
        for name, spec in protocol["source_reports"].items()
    }

    milestone16 = evidence["milestone16"]
    trace = evidence["common_trace"]
    effect = evidence["effect_oracle"]
    substitution = evidence["tuple_substitution"]
    faulted_conditions = {
        trial["condition"]
        for trial in effect["trials"]
        if trial["native"]["claimed_recovered"]
        and not (trial["oracle"]["safe"] and trial["oracle"]["recovered"])
    }
    dimensions = {
        trial["native"]["dimension"] for trial in substitution["trials"]
    }
    protocols = {
        trial["native"]["protocol"] for trial in substitution["trials"]
    }
    inherited_eliminations = len(milestone16["novelty_eliminations"])
    gap_families = milestone16["candidate_decisions"][
        "trusted_attribute_binding"
    ]["gap_baseline_families"]
    disagreement_contexts = milestone16["candidate_decisions"][
        "independent_effect_observation"
    ]["disagreement_contexts"]
    rules = protocol["decision_rules"]
    sentinel = substitution["by_guardrail"]["sentinel"]
    always_deny = substitution["by_guardrail"]["always_deny"]

    tuple_retained = (
        len(gap_families) >= rules["required_gap_baseline_families"]
        and len(dimensions) >= rules["required_tuple_dimensions"]
        and sentinel["benign_utility"] == 12
        and sentinel["contained_attacks"] == 24
        and sentinel["benign_utility"] > always_deny["benign_utility"]
    )
    effect_retained = (
        len(disagreement_contexts)
        >= rules["required_native_disagreement_contexts"]
        and len(faulted_conditions)
        >= rules["required_controlled_effect_failure_classes"]
        and effect["oracle_summary"]["claimed_success_without_safe_recovery"] > 0
    )
    trace_supported = (
        trace["accepted"]
        and trace["summary"]["native_namespace_roundtrips"]
        == trace["summary"]["trace_count"]
    )
    candidate_decisions = {
        "common_action_effect_evidence_model": (
            "supporting_artifact_only" if trace_supported else "drop"
        ),
        "cross_layer_effect_correspondence": (
            "retain_as_primary_evaluation_candidate" if effect_retained else "drop"
        ),
        "minimal_assurance_cut_sets": "motivated_but_untested",
        "non_transitive_resource_transitions": "untested_hypothesis",
        "policy_to_execution_digest_seal": "enabling_control_not_novel_claim",
        "trusted_complete_tuple_construction": (
            "retain_as_mechanism_supported_candidate" if tuple_retained else "drop"
        ),
    }
    publication_ready = all(protocol["publication_gates"].values())
    extracted = {
        "gap_baseline_families": gap_families,
        "native_disagreement_contexts": disagreement_contexts,
        "common_trace_records": trace["summary"]["trace_count"],
        "controlled_effect_failure_classes": sorted(faulted_conditions),
        "claimed_success_without_safe_recovery": effect["oracle_summary"][
            "claimed_success_without_safe_recovery"
        ],
        "tuple_dimensions": sorted(dimensions),
        "tuple_protocol_labels": sorted(protocols),
        "sentinel_tuple_result": sentinel,
        "always_deny_tuple_result": always_deny,
    }
    expected = protocol["acceptance"]
    accepted = (
        len(evidence) == expected["verified_reports"]
        and inherited_eliminations == expected["inherited_prior_art_eliminations"]
        and len(faulted_conditions) == expected["controlled_effect_failure_classes"]
        and len(dimensions) == expected["tuple_dimensions"]
        and len(protocols) == expected["tuple_protocol_labels"]
        and candidate_decisions == expected["candidate_decisions"]
        and publication_ready == expected["publication_ready"]
    )
    report = {
        "schema_version": "sentinel.milestone20-claim-audit-report.v1",
        "protocol_sha256": _sha256(protocol_path),
        "verified_source_hashes": {
            name: spec["sha256"] for name, spec in protocol["source_reports"].items()
        },
        "inherited_prior_art_eliminations": inherited_eliminations,
        "prior_art_subtraction": protocol["prior_art_subtraction"],
        "extracted_evidence": extracted,
        "candidate_decisions": candidate_decisions,
        "publication_ready": publication_ready,
        "missing_publication_gates": [
            key for key, value in protocol["publication_gates"].items() if not value
        ],
        "recommended_framing": expected["recommended_framing"],
        "next_discriminating_evidence": [
            "realistic calendar promptware with benign hard negatives",
            "non-transitive URL/file transition enforcement",
            "matched published-defense reconstruction",
            "frozen adaptive attacks and held-out confirmation",
            "minimal cross-layer assurance cut sets",
        ],
        "accepted": accepted,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        json.dumps(
            {
                "accepted": accepted,
                "candidate_decisions": candidate_decisions,
                "publication_ready": publication_ready,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
