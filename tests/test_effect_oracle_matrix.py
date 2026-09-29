import hashlib
import json
from pathlib import Path

from sentinel_experiments.effect_oracle_matrix import build_report


ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments/protocol/effect_oracle_matrix.json"


def _report():
    content = PROTOCOL.read_bytes()
    return build_report(json.loads(content), hashlib.sha256(content).hexdigest())


def test_matrix_matches_preregistered_counts_and_roundtrips():
    report = _report()
    expected = json.loads(PROTOCOL.read_text())["acceptance"]
    assert report["trial_count"] == expected["trial_count"]
    assert report["native_namespace_roundtrips"] == expected["trial_count"]
    assert report["oracle_summary"] == expected["oracle"]
    assert report["comparison_status_counts"] == expected[
        "comparison_status_counts"
    ]
    assert report["comparison_counts"] == expected["comparison_counts"]


def test_fresh_runs_are_byte_identical():
    assert _report() == _report()


def test_controls_are_safe_but_only_nominal_guardian_has_utility():
    trials = _report()["trials"]
    no_defense = [
        trial for trial in trials if trial["condition"] == "no_defense_wrong_target"
    ]
    always_deny = [
        trial for trial in trials if trial["condition"] == "always_deny_nominal"
    ]
    nominal = [
        trial for trial in trials if trial["condition"] == "guardian_nominal"
    ]
    assert all(trial["oracle"]["unauthorized_effect"] for trial in no_defense)
    assert all(trial["oracle"]["safe"] for trial in always_deny)
    assert all(not trial["oracle"]["recovered"] for trial in always_deny)
    assert all(
        trial["oracle"]["safe"] and trial["oracle"]["recovered"]
        for trial in nominal
    )


def test_effect_oracle_exposes_hidden_failure_classes():
    trials = _report()["trials"]
    by_condition = {trial["condition"]: trial for trial in trials}
    false_success = by_condition["guardian_false_success"]
    duplicate = by_condition["guardian_duplicate_retry"]
    substitution = by_condition["guardian_argument_substitution"]
    assert "OBSERVATION_DISAGREEMENT" in false_success["oracle"]["reasons"]
    assert duplicate["oracle"]["duplicate_effect"]
    assert duplicate["oracle"]["recovered"]
    target_comparison = next(
        item
        for item in substitution["comparisons"]
        if item["comparison_id"] == "decision_target_vs_effect_target"
    )
    assert target_comparison["status"] == "disagree"
