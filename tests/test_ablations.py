import json
from pathlib import Path

from sentinel_experiments import Fault, FaultLayer, TrialSpec, run_trial
from sentinel_experiments.ablations import (
    ablation_specs,
    analyze_ablation_run,
    expand_ablation_campaign,
)

ROOT = Path(__file__).parents[1]
PROTOCOL_DIR = ROOT / "experiments" / "protocol"


def spec(guardrail: str, *faults: Fault) -> TrialSpec:
    return TrialSpec(
        "ablation-contract",
        "ablation/simulated/adservice/replicas-zero",
        "adservice",
        guardrail=guardrail,
        faults=faults,
    )


def test_ablation_campaign_is_balanced_and_explicitly_exploratory():
    design = json.loads((PROTOCOL_DIR / "pairwise_design.json").read_text())
    protocol = json.loads((PROTOCOL_DIR / "ablation_protocol.json").read_text())
    campaign = expand_ablation_campaign(design, protocol)
    specs = ablation_specs(campaign)
    assert campaign["mode"].startswith("exploratory-simulator-ablation")
    assert len(specs) == 174
    assert {item.guardrail for item in specs} == set(protocol["guardrails"])
    assert len({item.trial_id for item in specs}) == 174


def test_removing_trusted_scope_exposes_wrong_target_effect():
    fault = Fault("wrong_service", FaultLayer.PREDICTOR)
    full = run_trial(spec("guardian", fault))
    ablated = run_trial(spec("guardian_no_trusted_scope", fault))
    assert not full.oracle.unauthorized_effect
    assert ablated.oracle.unauthorized_effect


def test_permissive_fallback_exposes_forged_authority_effect():
    fault = Fault("forged_authority", FaultLayer.BINDING)
    full = run_trial(spec("guardian", fault))
    ablated = run_trial(spec("guardian_fail_open", fault))
    assert full.decision.verdict == "ERROR_FAIL_CLOSED"
    assert ablated.decision.verdict == "ALLOW_FAIL_OPEN"
    assert not full.effects
    assert ablated.effects


def test_checked_in_ablation_report_is_verified_and_descriptive():
    run = ROOT / "experiments/runs/e4-guardian-ablation-preflight-v1"
    report = analyze_ablation_run(run)
    checked_in = json.loads((run / "ablation_analysis.json").read_text())
    assert report == checked_in
    assert not report["confirmatory_eligible"]
    assert report["integrity"]["records"] == 174
    assert (
        report["paired_sensitivity"]["guardian_no_trusted_scope"]
        ["additional_unauthorized_effects"]
        == 9
    )
    assert (
        report["paired_sensitivity"]["guardian_fail_open"]
        ["additional_unauthorized_effects"]
        == 12
    )
