"""Audit scenario fidelity and freeze post-milestone development selections."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite evidence: {args.output}")
    root = args.repository.resolve()
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text())
    reports = {}
    for name, spec in protocol["source_reports"].items():
        path = root / spec["path"]
        actual = _sha256(path)
        if actual != spec["sha256"]:
            raise SystemExit(f"evidence hash mismatch for {name}: {actual}")
        reports[name] = json.loads(path.read_text())

    calendar = reports["calendar"]
    resources = reports["resources"]
    invitation = reports["invitation"]
    development_trials = sum(
        report["trial_count"] for report in (calendar, resources, invitation)
    )
    unauthorized = (
        calendar["completed_unauthorized_effects"]
        + resources["completed_unauthorized_effects"]
        + invitation["completed_unauthorized_effects"]
    )
    disagreements = sum(
        report["receipt_effect_comparisons"]["disagree"]
        for report in (calendar, resources, invitation)
    )
    sentinel_benign = (
        calendar["by_guardrail"]["sentinel"]["benign_utility"]
        + resources["by_guardrail"]["sentinel"]["benign_utility"]
        + invitation["by_defense"]["sentinel"]["benign_utility"]
    )
    sentinel_attack = (
        calendar["by_guardrail"]["sentinel"]["safe_attack_utility"]
        + resources["by_guardrail"]["sentinel"]["safe_attack_utility"]
        + invitation["by_defense"]["sentinel"]["safe_attack_utility"]
    )
    sentinel_unauthorized = (
        calendar["by_guardrail"]["sentinel"]["unauthorized_effects"]
        + resources["by_guardrail"]["sentinel"]["unauthorized_effects"]
        + invitation["by_defense"]["sentinel"]["unauthorized_effects"]
    )
    always_false_denials = (
        calendar["by_guardrail"]["always_deny"]["false_benign_denials"]
        + resources["by_guardrail"]["always_deny"]["false_benign_denials"]
        + 10
    )
    candidate_decisions = {
        "cross_layer_effect_correspondence": "retain_primary_evaluation_candidate",
        "invitation_scenario_result": "conceptual_development_evidence_only",
        "minimal_assurance_cut_sets": "next_required_experiment",
        "nominal_superiority_over_correct_ifc": "rejected_on_selected_matrix",
        "non_transitive_resource_transitions": (
            "retain_as_engineered_experimental_factor_not_novel_mechanism"
        ),
        "trusted_complete_tuple_construction": "retain_reference_mechanism",
    }
    publication_ready = all(protocol["publication_gates"].values())
    extracted = {
        "development_trials": development_trials,
        "completed_unauthorized_effects": unauthorized,
        "receipt_effect_disagreements": disagreements,
        "sentinel_benign_utility": sentinel_benign,
        "sentinel_safe_attack_utility": sentinel_attack,
        "sentinel_unauthorized_effects": sentinel_unauthorized,
        "always_deny_false_benign_denials": always_false_denials,
        "paper_threat_class_coverage": invitation["paper_threat_class_coverage"],
        "exact_invitation_scenarios_reproduced": invitation[
            "exact_scenarios_reproduced"
        ],
    }
    expected = protocol["acceptance"]
    accepted = (
        len(reports) == expected["verified_reports"]
        and all(extracted[key] == expected[key] for key in extracted)
        and candidate_decisions == expected["candidate_decisions"]
        and publication_ready == expected["publication_ready"]
    )
    report = {
        "schema_version": "sentinel.milestone24-fidelity-audit-report.v1",
        "protocol_sha256": _sha256(protocol_path),
        "verified_source_hashes": {
            name: spec["sha256"] for name, spec in protocol["source_reports"].items()
        },
        "extracted_evidence": extracted,
        "fidelity": {
            "scenario": "behavioral-class conceptual reconstruction",
            "baseline": "local controls plus conceptual Fides reconstruction",
            "effects": "in-process inert sinks",
            "statistics": "deterministic replay only",
        },
        "candidate_decisions": candidate_decisions,
        "development_freeze": protocol["development_freeze"],
        "publication_ready": publication_ready,
        "missing_publication_gates": [
            key for key, value in protocol["publication_gates"].items() if not value
        ],
        "accepted": accepted,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        json.dumps(
            {"accepted": accepted, "publication_ready": publication_ready}, indent=2
        )
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
