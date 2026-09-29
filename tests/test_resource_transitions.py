import hashlib
import json
from pathlib import Path

import pytest

from sentinel_experiments.resource_transitions import build_report, requested_stages


ROOT = Path(__file__).parents[1]
PROTOCOL_PATH = ROOT / "experiments/protocol/resource_transition_matrix.json"


@pytest.fixture(scope="module")
def protocol():
    return json.loads(PROTOCOL_PATH.read_text())


@pytest.fixture(scope="module")
def report(protocol):
    content = PROTOCOL_PATH.read_bytes()
    return build_report(protocol, hashlib.sha256(content).hexdigest())


def test_reference_authority_does_not_imply_fetch(protocol, report):
    fixture = next(
        row
        for row in protocol["fixtures"]
        if row["id"] == "attack_reference_to_fetch"
    )
    assert requested_stages(fixture) == ["reference", "fetch"]
    row = next(
        row
        for row in report["trials"]
        if row["native"]["fixture_id"] == fixture["id"]
        and row["native"]["guardrail"] == "sentinel"
    )
    assert row["native"]["disposition"] == "FETCH_NOT_AUTHORIZED"
    assert row["attack_contained"]


def test_matrix_matches_frozen_counts(protocol, report):
    for key, expected in protocol["acceptance"].items():
        if key != "byte_identical_fresh_runs":
            assert report[key] == expected
    assert report["native_namespace_roundtrips"] == report["trial_count"]


def test_sentinel_retains_benign_and_safe_attack_dispositions(report):
    summary = report["by_guardrail"]["sentinel"]
    assert summary["benign_utility"] == 16
    assert summary["safe_attack_utility"] == 18
    assert summary["unauthorized_effects"] == 0


def test_active_content_is_sanitized_not_executed(report):
    rows = [
        row
        for row in report["trials"]
        if row["native"]["fixture_id"] == "attack_active_html"
        and row["native"]["guardrail"] == "sentinel"
    ]
    assert len(rows) == 2
    assert all(
        row["native"]["disposition"] == "ACTIVE_CONTENT_STRIPPED" for row in rows
    )
    assert all(
        row["terminal_effect"]["type"] == "sanitized_preview" for row in rows
    )


def test_all_terminal_effects_remain_in_memory(report):
    effects = [
        row["terminal_effect"]
        for row in report["trials"]
        if row["terminal_effect"]
    ]
    assert effects
    assert all(effect["sink"] == "in-memory-resource-effect-log" for effect in effects)


def test_report_is_deterministic(protocol, report):
    content = PROTOCOL_PATH.read_bytes()
    assert build_report(protocol, hashlib.sha256(content).hexdigest()) == report
