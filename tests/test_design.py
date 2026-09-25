import json
from pathlib import Path

from sentinel_experiments.design import (
    generate_pairwise_design,
    uncovered_cross_layer_pairs,
)

ROOT = Path(__file__).parents[1]
PROTOCOL_DIR = ROOT / "experiments" / "protocol"


def inputs():
    catalog = json.loads((PROTOCOL_DIR / "fault_catalog.json").read_text())
    protocol = json.loads(
        (PROTOCOL_DIR / "confirmatory_protocol.json").read_text()
    )
    return catalog, protocol


def test_pairwise_design_is_deterministic_and_complete():
    catalog, protocol = inputs()
    first = generate_pairwise_design(catalog, protocol)
    second = generate_pairwise_design(catalog, protocol)
    assert first == second
    assert not uncovered_cross_layer_pairs(catalog, first)
    assert first["coverage"] == {
        "operators": 11,
        "cross_layer_pairs_required": 46,
        "cross_layer_pairs_covered": 46,
    }


def test_pairwise_design_has_nominal_singles_and_exact_pairs():
    catalog, protocol = inputs()
    design = generate_pairwise_design(catalog, protocol)
    kinds = [row["kind"] for row in design["rows"]]
    assert kinds.count("nominal") == 1
    assert kinds.count("single") == 11
    assert kinds.count("pair") == 46
    assert len({tuple(row["faults"]) for row in design["rows"]}) == 58


def test_trial_budget_includes_all_frozen_systems_and_guardrails():
    catalog, protocol = inputs()
    design = generate_pairwise_design(catalog, protocol)
    assert "always_deny" in protocol["guardrails"]
    assert design["trial_budget_per_repetition"] == 580


def test_checked_in_design_matches_generator():
    catalog, protocol = inputs()
    checked_in = json.loads((PROTOCOL_DIR / "pairwise_design.json").read_text())
    assert checked_in == generate_pairwise_design(catalog, protocol)
