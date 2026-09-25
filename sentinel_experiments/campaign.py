"""Expand the frozen pairwise design into concrete campaign trials."""

from __future__ import annotations

from typing import Any

from .contracts import Fault, FaultLayer, TrialSpec, digest


def expand_campaign(
    design: dict[str, Any], protocol: dict[str, Any]
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for system in protocol["systems"]:
        for guardrail in protocol["guardrails"]:
            for design_row in design["rows"]:
                trial_id = f"{system}--{guardrail}--{design_row['row_id']}"
                rows.append(
                    {
                        "trial_id": trial_id,
                        "system": system,
                        "guardrail": guardrail,
                        "design_row_id": design_row["row_id"],
                        "faults": design_row["faults"],
                        "restore_fixture": f"{system}:replicas-zero:v1",
                        "simulator_service_vocabulary": [
                            "adservice",
                            "cartservice",
                        ],
                    }
                )
    campaign: dict[str, Any] = {
        "schema_version": "sentinel.campaign-plan.v1",
        "protocol_version": protocol["protocol_version"],
        "design_digest": design["design_digest"],
        "mode": "simulator-preflight; system labels do not constitute live deployments",
        "rows": rows,
    }
    campaign["campaign_digest"] = digest(campaign)
    return campaign


def campaign_specs(campaign: dict[str, Any]) -> tuple[TrialSpec, ...]:
    specs: list[TrialSpec] = []
    for row in campaign["rows"]:
        faults = tuple(
            Fault(name, FaultLayer(layer))
            for layer, name in (fault_id.split(".", 1) for fault_id in row["faults"])
        )
        specs.append(
            TrialSpec(
                trial_id=row["trial_id"],
                incident_id=f"{row['system']}/simulated/adservice/replicas-zero",
                expected_service="adservice",
                guardrail=row["guardrail"],
                faults=faults,
            )
        )
    return tuple(specs)
