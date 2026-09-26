"""Strict reconciliation of broker receipts with Kubernetes audit events."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import parse_qs, urlsplit

from .contracts import ExecutionReceipt, digest


@dataclass(frozen=True)
class KubernetesAuditWrite:
    audit_id: str
    stage: str
    verb: str
    username: str
    namespace: str
    deployment: str
    subresource: str
    replicas: int
    response_code: int
    correlation_id: str
    request_uri: str

    @property
    def completed(self) -> bool:
        return 200 <= self.response_code < 300 and self.stage == "ResponseComplete"


@dataclass(frozen=True)
class AuditReconciliation:
    schema_version: str
    complete: bool
    submitted_receipts: int
    audit_events: int
    matched_attempts: int
    duplicate_semantic_writes: bool
    unmatched_receipt_ids: tuple[str, ...]
    unexpected_audit_ids: tuple[str, ...]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["reconciliation_digest"] = digest(value)
        return value


def parse_kubernetes_audit_write(payload: str | dict[str, Any]) -> KubernetesAuditWrite:
    value = json.loads(payload) if isinstance(payload, str) else payload
    if value.get("apiVersion") != "audit.k8s.io/v1" or value.get("kind") != "Event":
        raise ValueError("unsupported Kubernetes audit event")
    reference = value.get("objectRef", {})
    if reference.get("resource") != "deployments" or reference.get("subresource") != "scale":
        raise ValueError("audit event is not a Deployment scale write")
    request_uri = value["requestURI"]
    query = parse_qs(urlsplit(request_uri).query)
    field_managers = query.get("fieldManager", [])
    if len(field_managers) != 1 or not field_managers[0].startswith("sentinel-"):
        raise ValueError("audit event lacks a unique SENTINEL correlation ID")
    request = value.get("requestObject", {})
    replicas = request.get("spec", {}).get("replicas")
    if isinstance(replicas, bool) or not isinstance(replicas, int) or replicas < 0:
        raise ValueError("audit event has an invalid replica request")
    response_code = value.get("responseStatus", {}).get("code")
    if not isinstance(response_code, int):
        raise TypeError("audit event lacks a response code")
    return KubernetesAuditWrite(
        audit_id=value["auditID"],
        stage=value["stage"],
        verb=value["verb"],
        username=value["user"]["username"],
        namespace=reference["namespace"],
        deployment=reference["name"],
        subresource=reference["subresource"],
        replicas=replicas,
        response_code=response_code,
        correlation_id=field_managers[0],
        request_uri=request_uri,
    )


def reconcile_execution_audit(
    receipts: tuple[ExecutionReceipt, ...],
    events: tuple[KubernetesAuditWrite, ...],
    *,
    expected_namespace: str,
    expected_username: str,
) -> AuditReconciliation:
    reasons: list[str] = []
    submitted = tuple(receipt for receipt in receipts if receipt.submitted)
    receipt_by_correlation = {
        receipt.correlation_id: receipt
        for receipt in submitted
        if receipt.correlation_id is not None
    }
    if len(receipt_by_correlation) != len(submitted):
        reasons.append("MISSING_OR_DUPLICATE_RECEIPT_CORRELATION")
    event_by_correlation = {event.correlation_id: event for event in events}
    if len(event_by_correlation) != len(events):
        reasons.append("DUPLICATE_AUDIT_CORRELATION")
    if len({event.audit_id for event in events}) != len(events):
        reasons.append("DUPLICATE_AUDIT_ID")

    unmatched: list[str] = []
    matched = 0
    for correlation_id, receipt in receipt_by_correlation.items():
        event = event_by_correlation.get(correlation_id)
        if event is None:
            unmatched.append(receipt.receipt_id)
            continue
        event_valid = True
        if event.username != expected_username:
            reasons.append(f"UNEXPECTED_ACTOR:{event.audit_id}")
            event_valid = False
        if event.namespace != expected_namespace:
            reasons.append(f"UNEXPECTED_NAMESPACE:{event.audit_id}")
            event_valid = False
        if event.verb not in {"patch", "update"}:
            reasons.append(f"UNEXPECTED_VERB:{event.audit_id}")
            event_valid = False
        if (
            event.deployment != receipt.executed_service
            or event.replicas != receipt.replicas
        ):
            reasons.append(f"SEMANTIC_MISMATCH:{event.audit_id}")
            event_valid = False
        if event.completed != receipt.completed:
            reasons.append(f"COMPLETION_MISMATCH:{event.audit_id}")
            event_valid = False
        if event_valid:
            matched += 1

    expected_correlations = set(receipt_by_correlation)
    unexpected = sorted(
        event.audit_id
        for event in events
        if event.correlation_id not in expected_correlations
    )
    if unmatched:
        reasons.append("MISSING_AUDIT_EVENT")
    if unexpected:
        reasons.append("UNEXPECTED_AUDIT_EVENT")
    audit_semantics = Counter(
        (event.deployment, event.replicas)
        for event in events
        if event.completed and event.correlation_id in expected_correlations
    )
    duplicate = any(count > 1 for count in audit_semantics.values())
    return AuditReconciliation(
        schema_version="sentinel.audit-reconciliation.v1",
        complete=not reasons,
        submitted_receipts=len(submitted),
        audit_events=len(events),
        matched_attempts=matched,
        duplicate_semantic_writes=duplicate,
        unmatched_receipt_ids=tuple(sorted(unmatched)),
        unexpected_audit_ids=tuple(unexpected),
        reasons=tuple(sorted(set(reasons))),
    )


def reconcile_pilot_record(
    record: dict[str, Any],
    events: tuple[KubernetesAuditWrite, ...],
    *,
    expected_namespace: str,
    expected_username: str,
) -> dict[str, Any]:
    unsigned = dict(record)
    record_digest = unsigned.pop("record_digest", None)
    if not isinstance(record_digest, str) or digest(unsigned) != record_digest:
        raise ValueError("pilot record digest mismatch")
    trial = record.get("trial")
    if not isinstance(trial, dict):
        raise TypeError("pilot record has no live trial")
    receipts = tuple(
        ExecutionReceipt(**receipt) for receipt in trial["execution_receipts"]
    )
    reconciliation = reconcile_execution_audit(
        receipts,
        events,
        expected_namespace=expected_namespace,
        expected_username=expected_username,
    )
    report: dict[str, Any] = {
        "schema_version": "sentinel.pilot-audit-report.v1",
        "pilot_record_digest": record_digest,
        "reconciliation": reconciliation.to_dict(),
        "evidence_class": "fixture_contract_or_live_candidate",
    }
    report["report_digest"] = digest(report)
    return report
