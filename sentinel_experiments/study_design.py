"""Audit the preregistered census/confirmatory study partition."""

from __future__ import annotations

from typing import Any

from .contracts import digest


def audit_study_partition(
    design: dict[str, Any],
    protocol: dict[str, Any],
    partition: dict[str, Any],
) -> dict[str, Any]:
    rows = {row["row_id"]: row for row in design["rows"]}
    if partition["design_digest"] != design["design_digest"]:
        raise ValueError("study partition references the wrong design digest")
    if partition["amends_protocol_version"] != protocol["protocol_version"]:
        raise ValueError("study partition references the wrong protocol version")

    nominal_and_singles = {
        row_id for row_id, row in rows.items() if row["kind"] in {"nominal", "single"}
    }
    pilot_rows = partition["pilot"]["row_ids"]
    confirmatory_rows = partition["confirmatory_subset"]["row_ids"]
    if len(pilot_rows) != len(set(pilot_rows)):
        raise ValueError("pilot contains duplicate row IDs")
    if len(confirmatory_rows) != len(set(confirmatory_rows)):
        raise ValueError("confirmatory subset contains duplicate row IDs")
    if set(pilot_rows) != nominal_and_singles:
        raise ValueError("pilot must contain exactly nominal and every single fault")
    if not set(confirmatory_rows) <= set(rows):
        raise ValueError("confirmatory subset references an unknown design row")
    if not nominal_and_singles <= set(confirmatory_rows):
        raise ValueError("confirmatory subset must retain nominal and all singles")

    singleton_by_fault = {
        row["faults"][0]: row_id
        for row_id, row in rows.items()
        if row["kind"] == "single"
    }
    selected_pairs = [
        rows[row_id]
        for row_id in confirmatory_rows
        if rows[row_id]["kind"] == "pair"
    ]
    for row in selected_pairs:
        missing = {
            singleton_by_fault[fault]
            for fault in row["faults"]
            if singleton_by_fault[fault] not in confirmatory_rows
        }
        if missing:
            raise ValueError(
                f"selected pair {row['row_id']} lacks component singles: {missing}"
            )

    rationales = partition["confirmatory_subset"]["selected_pair_rationales"]
    selected_pair_ids = {row["row_id"] for row in selected_pairs}
    if set(rationales) != selected_pair_ids:
        raise ValueError("every selected pair requires exactly one frozen rationale")
    if partition["data_separation"]["record_reuse_across_phases"]:
        raise ValueError("pilot/census records cannot enter primary inference")
    if not partition["pilot"]["guardrail_condition_labels_masked"]:
        raise ValueError("pilot must mask guardrail-condition labels")
    if partition["pilot"]["primary_contrasts_evaluated"]:
        raise ValueError("pilot cannot evaluate primary contrasts")
    if partition["pilot"]["eligible_for_primary_inference"]:
        raise ValueError("pilot records cannot enter primary inference")
    if partition["fault_surface_census"]["eligible_for_primary_inference"]:
        raise ValueError("census records cannot enter primary inference")
    if not partition["confirmatory_subset"]["eligible_for_primary_inference"]:
        raise ValueError("confirmatory records must be marked inference-eligible")
    prefixes = partition["data_separation"]["run_id_prefixes"]
    if len(set(prefixes.values())) != 3:
        raise ValueError("each phase requires a distinct run ID prefix")
    if (
        partition["pilot"]["minimum_independent_deployment_blocks_per_system"] < 3
        or partition["confirmatory_subset"][
            "minimum_independent_deployment_blocks_per_system"
        ]
        < 3
    ):
        raise ValueError("pilot and confirmatory phases require at least three blocks")

    systems = len(protocol["systems"])
    guardrails = len(protocol["guardrails"])
    pilot_cells = len(pilot_rows) * systems * guardrails
    confirmatory_cells = len(confirmatory_rows) * systems * guardrails
    census_cells = len(rows) * systems * guardrails
    pair_layers = sorted(
        {
            fault.split(".", 1)[0]
            for row in selected_pairs
            for fault in row["faults"]
        }
    )
    report: dict[str, Any] = {
        "schema_version": "sentinel.study-partition-audit.v1",
        "partition_version": partition["partition_version"],
        "design_digest_verified": True,
        "protocol_version_verified": True,
        "rows": {
            "frozen_design": len(rows),
            "pilot": len(pilot_rows),
            "census": len(rows),
            "confirmatory": len(confirmatory_rows),
            "confirmatory_pairs": len(selected_pairs),
        },
        "cells_per_complete_block": {
            "pilot": pilot_cells,
            "census": census_cells,
            "confirmatory": confirmatory_cells,
        },
        "selected_pair_layers": pair_layers,
        "component_singles_present": True,
        "pilot_condition_labels_masked": True,
        "primary_inference_phases": ["confirmatory"],
        "phase_record_reuse": False,
        "sample_size_status": "pending blinded live pilot",
        "limitations": [
            "The audit validates design structure, not statistical power.",
            "Pilot variance and event rates do not exist until live execution.",
            "The seven selected pairs test prespecified causal pathways, not all interactions.",
            "The full 58-row census remains descriptive and excluded from primary inference.",
        ],
    }
    report["audit_digest"] = digest(report)
    return report
