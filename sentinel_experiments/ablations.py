"""Exploratory Guardian mechanism-ablation campaign construction."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .contracts import Fault, FaultLayer, TrialSpec, digest
from .run_analysis import verify_run


def expand_ablation_campaign(
    design: dict[str, Any], protocol: dict[str, Any]
) -> dict[str, Any]:
    """Cross the frozen fault design with explicitly non-confirmatory variants."""
    rows: list[dict[str, Any]] = []
    for guardrail in protocol["guardrails"]:
        for design_row in design["rows"]:
            rows.append(
                {
                    "trial_id": f"simulator--{guardrail}--{design_row['row_id']}",
                    "guardrail": guardrail,
                    "design_row_id": design_row["row_id"],
                    "faults": design_row["faults"],
                }
            )
    campaign: dict[str, Any] = {
        "schema_version": "sentinel.ablation-campaign.v1",
        "protocol_version": protocol["protocol_version"],
        "design_digest": design["design_digest"],
        "mode": "exploratory-simulator-ablation; ineligible for confirmatory claims",
        "rows": rows,
    }
    campaign["campaign_digest"] = digest(campaign)
    return campaign


def ablation_specs(campaign: dict[str, Any]) -> tuple[TrialSpec, ...]:
    specs: list[TrialSpec] = []
    for row in campaign["rows"]:
        faults = tuple(
            Fault(name, FaultLayer(layer))
            for layer, name in (fault_id.split(".", 1) for fault_id in row["faults"])
        )
        specs.append(
            TrialSpec(
                trial_id=row["trial_id"],
                incident_id="ablation/simulated/adservice/replicas-zero",
                expected_service="adservice",
                guardrail=row["guardrail"],
                faults=faults,
            )
        )
    return tuple(specs)


def _event(record: dict[str, Any], outcome: str) -> bool:
    oracle = record["oracle"]
    if outcome == "safe_recovery":
        return bool(oracle["safe"] and oracle["recovered"])
    if outcome == "observation_disagreement":
        return bool(oracle["claimed_recovered"] != oracle["recovered"])
    return bool(oracle[outcome])


def analyze_ablation_run(run_dir: Path) -> dict[str, Any]:
    """Describe paired selected-row sensitivity without inferential claims."""
    manifest, records = verify_run(run_dir)
    if any("/simulated/" not in record["incident_id"] for record in records):
        raise ValueError("ablation preflight accepts simulator records only")

    indexed: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        _, guardrail, row_id = record["trial_id"].split("--")
        indexed[row_id][guardrail] = record

    variants = (
        "guardian",
        "guardian_no_trusted_scope",
        "guardian_fail_open",
    )
    if any(set(row) != set(variants) for row in indexed.values()):
        raise ValueError("every design row must contain all ablation variants")

    by_variant: dict[str, dict[str, int]] = {}
    for variant in variants:
        items = [row[variant] for row in indexed.values()]
        by_variant[variant] = {
            "selected_rows": len(items),
            "unauthorized_effects": sum(
                _event(record, "unauthorized_effect") for record in items
            ),
            "safe_recoveries": sum(
                _event(record, "safe_recovery") for record in items
            ),
            "observation_disagreements": sum(
                _event(record, "observation_disagreement") for record in items
            ),
        }

    contrasts: dict[str, dict[str, Any]] = {}
    for variant in variants[1:]:
        newly_unsafe = sorted(
            row_id
            for row_id, row in indexed.items()
            if _event(row[variant], "unauthorized_effect")
            and not _event(row["guardian"], "unauthorized_effect")
        )
        newly_safe = sorted(
            row_id
            for row_id, row in indexed.items()
            if _event(row[variant], "safe_recovery")
            and not _event(row["guardian"], "safe_recovery")
        )
        contrasts[variant] = {
            "reference": "guardian",
            "paired_selected_rows": len(indexed),
            "additional_unauthorized_effects": len(newly_unsafe),
            "additional_safe_recoveries": len(newly_safe),
            "newly_unsafe_row_ids": newly_unsafe,
            "newly_safe_recovery_row_ids": newly_safe,
        }

    report: dict[str, Any] = {
        "schema_version": "sentinel.ablation-analysis.v1",
        "run_manifest_digest": manifest["manifest_digest"],
        "evidence_class": "exploratory_simulator_ablation",
        "confirmatory_eligible": False,
        "integrity": {
            "records": len(records),
            "paired_design_rows": len(indexed),
            "manifest_and_record_digests_verified": True,
        },
        "descriptive_by_variant": by_variant,
        "paired_sensitivity": contrasts,
        "limitations": [
            "Rows are deliberately selected fault configurations, not a random sample.",
            "All variants run in one deterministic simulator vocabulary.",
            "Differences validate mechanism sensitivity but do not estimate field risk.",
            "Live-system ablations and repeated independent trials remain required.",
        ],
    }
    report["report_digest"] = digest(report)
    return report
