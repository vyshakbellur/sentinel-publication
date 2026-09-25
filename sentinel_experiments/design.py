"""Deterministic experiment-design generation and coverage checks."""

from __future__ import annotations

from itertools import combinations
from typing import Any

from .contracts import digest


def generate_pairwise_design(
    catalog: dict[str, Any], protocol: dict[str, Any]
) -> dict[str, Any]:
    """Cover every cross-layer operator pair plus nominal and single faults."""
    operators = sorted(catalog["operators"], key=lambda item: item["id"])
    singles = [(operator["id"],) for operator in operators]
    pairs = [
        tuple(sorted((left["id"], right["id"])))
        for left, right in combinations(operators, 2)
        if left["layer"] != right["layer"]
    ]
    fault_sets = [(), *singles, *sorted(set(pairs))]
    rows = [
        {
            "row_id": f"PW{index:03d}",
            "kind": "nominal" if not faults else "single" if len(faults) == 1 else "pair",
            "faults": list(faults),
        }
        for index, faults in enumerate(fault_sets)
    ]
    systems = protocol["systems"]
    guardrails = protocol["guardrails"]
    design: dict[str, Any] = {
        "schema_version": "sentinel.pairwise-design.v1",
        "catalog_version": catalog["catalog_version"],
        "protocol_version": protocol["protocol_version"],
        "strategy": "nominal + every single operator + every exact cross-layer operator pair",
        "rows": rows,
        "coverage": {
            "operators": len(operators),
            "cross_layer_pairs_required": len(pairs),
            "cross_layer_pairs_covered": len(set(pairs)),
        },
        "trial_budget_per_repetition": len(rows) * len(systems) * len(guardrails),
        "repetitions": None,
    }
    design["design_digest"] = digest(design)
    return design


def uncovered_cross_layer_pairs(
    catalog: dict[str, Any], design: dict[str, Any]
) -> set[tuple[str, str]]:
    operators = catalog["operators"]
    required = {
        tuple(sorted((left["id"], right["id"])))
        for left, right in combinations(operators, 2)
        if left["layer"] != right["layer"]
    }
    covered: set[tuple[str, str]] = set()
    for row in design["rows"]:
        for pair in combinations(row["faults"], 2):
            covered.add(tuple(sorted(pair)))
    return required - covered
