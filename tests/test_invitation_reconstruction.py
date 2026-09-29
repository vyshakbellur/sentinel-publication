import hashlib
import json
from pathlib import Path

import pytest

from sentinel_experiments.invitation_reconstruction import build_report


ROOT = Path(__file__).parents[1]
PROTOCOL_PATH = ROOT / "experiments/protocol/invitation_scenario_reconstruction.json"


@pytest.fixture(scope="module")
def protocol():
    return json.loads(PROTOCOL_PATH.read_text())


@pytest.fixture(scope="module")
def report(protocol):
    content = PROTOCOL_PATH.read_bytes()
    return build_report(protocol, hashlib.sha256(content).hexdigest())


def test_report_matches_frozen_counts(protocol, report):
    for key, expected in protocol["acceptance"].items():
        assert report[key] == expected
    assert report["native_namespace_roundtrips"] == report["trial_count"]


def test_class_coverage_is_not_exact_reproduction(report):
    assert report["paper_threat_class_coverage"] == 5
    assert report["behavioral_attack_analogs"] == 10
    assert report["exact_scenarios_reproduced"] == 0
    assert report["unsupported_exact_elements"]


def test_adapter_label_is_a_fides_reconstruction_assumption(report):
    correct = report["by_defense"]["fides_correct_label_reconstruction"]
    mislabeled = report["by_defense"]["fides_mislabeled_adapter_reconstruction"]
    assert correct["contained_attacks"] == 20
    assert mislabeled["contained_attacks"] == 0
    assert mislabeled["unauthorized_effects"] == 20


def test_sentinel_and_fides_reconstruction_tie_in_selected_matrix(report):
    assert report["by_defense"]["sentinel"] == report["by_defense"][
        "fides_correct_label_reconstruction"
    ]


def test_every_effect_is_inert(report):
    effects = [row["effect"] for row in report["trials"] if row["effect"]]
    assert effects
    assert all(
        effect["sink"] == "in-memory-invitation-effect-log" for effect in effects
    )


def test_report_is_deterministic(protocol, report):
    content = PROTOCOL_PATH.read_bytes()
    assert build_report(protocol, hashlib.sha256(content).hexdigest()) == report
