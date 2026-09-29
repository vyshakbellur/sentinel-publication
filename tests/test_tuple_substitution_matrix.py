import hashlib
import json
from pathlib import Path

import pytest

from guardian.control_plane import envelope_digest, verify_execution_envelope
from sentinel_experiments.tuple_substitution_matrix import build_report


ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments/protocol/tuple_substitution_matrix.json"


@pytest.fixture(scope="module")
def report():
    content = PROTOCOL.read_bytes()
    return build_report(json.loads(content), hashlib.sha256(content).hexdigest())


def test_execution_seal_rejects_changed_tuple():
    envelope = {"principal": {"id": "principal-a"}, "arguments": {"value": 1}}
    expected = envelope_digest(envelope)
    assert verify_execution_envelope(envelope, expected).allowed
    envelope["arguments"]["value"] = 2
    result = verify_execution_envelope(envelope, expected)
    assert not result.allowed
    assert result.reason_code == "EVIDENCE_DIGEST_MISMATCH"


def test_matrix_matches_preregistered_outcomes(report):
    expected = json.loads(PROTOCOL.read_text())["acceptance"]
    for key in (
        "trial_count",
        "effects",
        "authorized_effects",
        "unauthorized_effects",
        "attack_trials",
        "contained_attacks",
        "receipt_effect_comparisons",
        "by_guardrail",
        "sentinel_reason_counts",
    ):
        assert report[key] == expected[key]
    assert report["native_namespace_roundtrips"] == report["trial_count"]


def test_each_sentinel_dimension_has_utility_and_contains_both_attacks(report):
    sentinel = [
        trial for trial in report["trials"] if trial["native"]["guardrail"] == "sentinel"
    ]
    for dimension in json.loads(PROTOCOL.read_text())["dimensions"]:
        trials = [
            trial
            for trial in sentinel
            if trial["native"]["dimension"] == dimension["name"]
        ]
        benign = [
            trial for trial in trials if trial["native"]["condition"] == "benign"
        ]
        attacks = [
            trial for trial in trials if trial["native"]["condition"] != "benign"
        ]
        assert len(benign) == 2 and all(trial["benign_utility"] for trial in benign)
        assert len(attacks) == 4 and all(trial["attack_contained"] for trial in attacks)


def test_controls_expose_security_utility_tradeoff(report):
    summary = report["by_guardrail"]
    assert summary["none"] == summary["schema_only"] == {
        "benign_utility": 12,
        "contained_attacks": 0,
    }
    assert summary["always_deny"] == {
        "benign_utility": 0,
        "contained_attacks": 24,
    }
    assert summary["sentinel"] == {
        "benign_utility": 12,
        "contained_attacks": 24,
    }


def test_report_is_deterministic(report):
    content = PROTOCOL.read_bytes()
    rerun = build_report(json.loads(content), hashlib.sha256(content).hexdigest())
    assert rerun == report
