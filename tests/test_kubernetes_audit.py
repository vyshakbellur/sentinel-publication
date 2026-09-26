import json
from dataclasses import replace
from pathlib import Path

import pytest

from sentinel_experiments.contracts import ExecutionReceipt, digest
from sentinel_experiments.kubernetes_audit import (
    parse_kubernetes_audit_write,
    reconcile_execution_audit,
    reconcile_pilot_record,
)

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests/fixtures/kubernetes"
USERNAME = "system:serviceaccount:sentinel-online-boutique:sentinel-actuator"


def event(name):
    return parse_kubernetes_audit_write((FIXTURES / name).read_text())


def receipt(attempt, correlation):
    return ExecutionReceipt(
        f"receipt-{attempt}",
        "action-1",
        attempt,
        "adservice",
        "adservice",
        2,
        True,
        True,
        correlation_id=correlation,
    )


def reconcile(receipts, events):
    return reconcile_execution_audit(
        tuple(receipts),
        tuple(events),
        expected_namespace="sentinel-online-boutique",
        expected_username=USERNAME,
    )


def test_scale_audit_event_parses_strict_correlation_and_semantics():
    parsed = event("audit_scale_adservice_1.json")
    assert parsed.correlation_id == "sentinel-attempt-001"
    assert parsed.deployment == "adservice" and parsed.replicas == 2
    assert parsed.completed


def test_one_receipt_reconciles_with_one_independent_audit_event():
    report = reconcile(
        [receipt(1, "sentinel-attempt-001")],
        [event("audit_scale_adservice_1.json")],
    )
    assert report.complete and report.matched_attempts == 1
    assert not report.duplicate_semantic_writes
    assert report.to_dict()["reconciliation_digest"]


def test_duplicate_attempts_require_two_unique_audit_events():
    report = reconcile(
        [
            receipt(1, "sentinel-attempt-001"),
            receipt(2, "sentinel-attempt-002"),
        ],
        [
            event("audit_scale_adservice_1.json"),
            event("audit_scale_adservice_2.json"),
        ],
    )
    assert report.complete and report.matched_attempts == 2
    assert report.duplicate_semantic_writes


def test_missing_extra_or_wrong_actor_event_fails_reconciliation():
    first = event("audit_scale_adservice_1.json")
    second = event("audit_scale_adservice_2.json")
    missing = reconcile(
        [receipt(1, "sentinel-attempt-001"), receipt(2, "sentinel-attempt-002")],
        [first],
    )
    assert not missing.complete and "MISSING_AUDIT_EVENT" in missing.reasons
    extra = reconcile([receipt(1, "sentinel-attempt-001")], [first, second])
    assert not extra.complete and "UNEXPECTED_AUDIT_EVENT" in extra.reasons
    wrong_actor = replace(first, username="system:serviceaccount:other:actor")
    actor = reconcile([receipt(1, "sentinel-attempt-001")], [wrong_actor])
    assert not actor.complete
    assert any(reason.startswith("UNEXPECTED_ACTOR") for reason in actor.reasons)


def test_dropped_receipt_requires_no_audit_write():
    dropped = replace(
        receipt(1, "sentinel-attempt-001"),
        submitted=False,
        completed=False,
        dropped=True,
    )
    report = reconcile([dropped], [])
    assert report.complete and report.matched_attempts == 0


def test_non_scale_or_uncorrelated_event_is_rejected():
    payload = json.loads((FIXTURES / "audit_scale_adservice_1.json").read_text())
    payload["objectRef"]["subresource"] = "status"
    with pytest.raises(ValueError, match="not a Deployment scale"):
        parse_kubernetes_audit_write(payload)
    payload["objectRef"]["subresource"] = "scale"
    payload["requestURI"] = payload["requestURI"].split("?", 1)[0]
    with pytest.raises(ValueError, match="correlation ID"):
        parse_kubernetes_audit_write(payload)


def test_content_digested_pilot_record_can_be_bound_to_audit_report():
    pilot = {
        "schema_version": "sentinel.live-pilot.v3",
        "trial": {
            "execution_receipts": [
                {
                    "receipt_id": "receipt-1",
                    "action_id": "action-1",
                    "attempt": 1,
                    "requested_service": "adservice",
                    "executed_service": "adservice",
                    "replicas": 2,
                    "submitted": True,
                    "completed": True,
                    "bypassed": False,
                    "dropped": False,
                    "correlation_id": "sentinel-attempt-001"
                }
            ]
        },
    }
    pilot["record_digest"] = digest(pilot)
    report = reconcile_pilot_record(
        pilot,
        (event("audit_scale_adservice_1.json"),),
        expected_namespace="sentinel-online-boutique",
        expected_username=USERNAME,
    )
    assert report["pilot_record_digest"] == pilot["record_digest"]
    assert report["reconciliation"]["complete"]
    pilot["trial"]["execution_receipts"][0]["replicas"] = 3
    with pytest.raises(ValueError, match="digest mismatch"):
        reconcile_pilot_record(
            pilot,
            (event("audit_scale_adservice_1.json"),),
            expected_namespace="sentinel-online-boutique",
            expected_username=USERNAME,
        )
