import json
from collections import Counter
from pathlib import Path

from sentinel_experiments.campaign import campaign_specs, expand_campaign

ROOT = Path(__file__).parents[1]
PROTOCOL_DIR = ROOT / "experiments" / "protocol"


def inputs():
    design = json.loads((PROTOCOL_DIR / "pairwise_design.json").read_text())
    protocol = json.loads(
        (PROTOCOL_DIR / "confirmatory_protocol.json").read_text()
    )
    return design, protocol


def test_campaign_expansion_is_complete_and_has_unique_trial_ids():
    design, protocol = inputs()
    campaign = expand_campaign(design, protocol)
    assert len(campaign["rows"]) == 580
    identifiers = [row["trial_id"] for row in campaign["rows"]]
    assert len(identifiers) == len(set(identifiers))
    combinations = Counter(
        (row["system"], row["guardrail"]) for row in campaign["rows"]
    )
    assert set(combinations.values()) == {58}


def test_every_campaign_row_declares_restoration_and_simulator_boundary():
    design, protocol = inputs()
    campaign = expand_campaign(design, protocol)
    assert campaign["mode"].startswith("simulator-preflight")
    assert all(row["restore_fixture"].endswith(":v1") for row in campaign["rows"])
    assert all(row["simulator_service_vocabulary"] for row in campaign["rows"])


def test_campaign_specs_preserve_identifiers_guardrails_and_faults():
    design, protocol = inputs()
    campaign = expand_campaign(design, protocol)
    specs = campaign_specs(campaign)
    assert len(specs) == 580
    assert {spec.guardrail for spec in specs} == set(protocol["guardrails"])
    assert {spec.trial_id for spec in specs} == {
        row["trial_id"] for row in campaign["rows"]
    }


def test_checked_in_campaign_matches_generator():
    design, protocol = inputs()
    checked_in = json.loads((PROTOCOL_DIR / "campaign_plan.json").read_text())
    assert checked_in == expand_campaign(design, protocol)
