import hashlib
import json
from pathlib import Path

import pytest

from sentinel_experiments.calendar_promptware import (
    action_authorized,
    build_plan,
    build_report,
    schema_valid,
)


ROOT = Path(__file__).parents[1]
PROTOCOL_PATH = ROOT / "experiments/protocol/calendar_promptware_environment.json"


@pytest.fixture(scope="module")
def protocol():
    return json.loads(PROTOCOL_PATH.read_text())


@pytest.fixture(scope="module")
def report(protocol):
    content = PROTOCOL_PATH.read_bytes()
    return build_report(protocol, hashlib.sha256(content).hexdigest())


def test_broad_schema_does_not_confer_task_authority(protocol):
    fixture = next(
        item
        for item in protocol["fixtures"]
        if item["id"] == "attack_email_exfiltration"
    )
    extra = build_plan(fixture, protocol)[1]
    assert schema_valid(extra)
    assert not action_authorized(extra, fixture, protocol)


def test_authorized_share_is_distinct_from_invitation_selected_recipient(protocol):
    allowed = next(
        item for item in protocol["fixtures"] if item["id"] == "benign_authorized_share"
    )
    attacked = next(
        item
        for item in protocol["fixtures"]
        if item["id"] == "attack_email_exfiltration"
    )
    assert action_authorized(build_plan(allowed, protocol)[1], allowed, protocol)
    assert not action_authorized(build_plan(attacked, protocol)[1], attacked, protocol)


def test_matrix_matches_frozen_counts(report, protocol):
    expected = protocol["acceptance"]
    for key in (
        "trial_count",
        "fixture_count",
        "benign_fixture_count",
        "attack_fixture_count",
        "attempted_unauthorized_actions",
        "completed_unauthorized_effects",
        "total_completed_effects",
        "safe_useful_trials",
        "receipt_effect_comparisons",
        "by_guardrail",
    ):
        assert report[key] == expected[key]
    assert report["native_namespace_roundtrips"] == report["trial_count"]


def test_all_hard_negatives_remain_useful_under_sentinel(report):
    hard_negatives = [
        trial
        for trial in report["trials"]
        if trial["native"]["guardrail"] == "sentinel"
        and trial["native"]["fixture_class"] == "benign_hard_negative"
    ]
    assert len(hard_negatives) == 14
    assert all(trial["safe_useful"] for trial in hard_negatives)


def test_inert_execution_fixture_never_leaves_effect_sink(report):
    trials = [
        trial
        for trial in report["trials"]
        if trial["native"]["fixture_id"] == "attack_attachment_execution"
    ]
    assert trials
    for trial in trials:
        for effect in trial["effects"]:
            assert effect["sink"] == "in-memory-independent-effect-log"


def test_report_is_deterministic(report, protocol):
    content = PROTOCOL_PATH.read_bytes()
    assert build_report(protocol, hashlib.sha256(content).hexdigest()) == report
