"""Hash-bound final publication and claim audit for the 28-step campaign."""

from __future__ import annotations

from typing import Any, Mapping

from .contracts import digest


def build_report(
    protocol: Mapping[str, Any],
    reports: Mapping[str, Mapping[str, Any]],
    protocol_sha256: str,
) -> dict[str, Any]:
    milestone24 = reports["milestone24"]
    adaptive = reports["adaptive25"]
    cutsets = reports["cutsets26"]
    challenge = reports["challenge27"]

    descriptive_trials = (
        milestone24["extracted_evidence"]["development_trials"]
        + adaptive["candidate_trial_count"]
        + cutsets["trial_count"]
        + challenge["trial_count"]
    )
    unauthorized = (
        milestone24["extracted_evidence"]["completed_unauthorized_effects"]
        + adaptive["completed_unauthorized_effects"]
        + cutsets["completed_unauthorized_effects"]
        + challenge["completed_unauthorized_effects"]
    )
    disagreements = (
        milestone24["extracted_evidence"]["receipt_effect_disagreements"]
        + adaptive["receipt_effect_comparisons"]["disagree"]
        + cutsets["receipt_effect_comparisons"]["disagree"]
        + challenge["receipt_effect_comparisons"]["disagree"]
    )
    publication_ready = all(protocol["publication_gates"].values())
    extracted = {
        "verified_source_reports": len(reports),
        "descriptive_development_trials": descriptive_trials,
        "completed_unauthorized_effect_observations": unauthorized,
        "receipt_effect_disagreements": disagreements,
        "published_effectiveness_numbers_reproduced": 0,
        "exact_invitation_scenarios_reproduced": milestone24[
            "extracted_evidence"
        ]["exact_invitation_scenarios_reproduced"],
        "valid_confirmatory_holdouts_evaluated": challenge[
            "valid_confirmatory_holdouts_evaluated"
        ],
        "sentinel_duplicate_effect_failures": challenge["sentinel_cases_failed"],
        "missing_publication_gate_count": sum(
            not value for value in protocol["publication_gates"].values()
        ),
        "publication_ready": publication_ready,
    }
    expected = protocol["acceptance"]
    accepted = (
        len(reports) == expected["verified_source_reports"]
        and all(extracted[key] == expected[key] for key in extracted)
        and reports["milestone16"]["publication_ready"] is False
        and reports["milestone20"]["publication_ready"] is False
        and reports["milestone24"]["publication_ready"] is False
        and cutsets["minimal_sentinel_prevention_cut_sets"]
        == [["sentinel_adapter_fault"], ["sentinel_broker_fault"]]
        and cutsets["minimal_sentinel_silent_cut_sets"]
        == [
            ["sentinel_adapter_fault", "sentinel_observer_fault"],
            ["sentinel_broker_fault", "sentinel_observer_fault"],
        ]
        and challenge["confirmatory_validity"]["valid_confirmatory_label"] is False
    )
    report = {
        "schema_version": "sentinel.milestone28-final-audit-report.v1",
        "protocol_sha256": protocol_sha256,
        "verified_source_hashes": {
            name: spec["sha256"] for name, spec in protocol["source_reports"].items()
        },
        "extracted_evidence": extracted,
        "aggregation_warning": protocol["aggregation_warning"],
        "reproduction_grades": protocol["reproduction_grades"],
        "claim_decisions": protocol["claim_decisions"],
        "publication_gates": protocol["publication_gates"],
        "missing_publication_gates": [
            name for name, value in protocol["publication_gates"].items() if not value
        ],
        "readiness_verdict": protocol["readiness_verdict"],
        "minimum_next_evidence": protocol["minimum_next_evidence"],
        "accepted": accepted,
    }
    report["report_digest"] = digest(report)
    return report
