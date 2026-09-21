"""
Guardian Forensics: Audit Trail

Implements Principle 4: "Leave a Mark Everywhere."
Every layer stamps metadata into a composite, auditable forensic trail.
Provides structured logging and SOC dashboard-ready output.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class AuditEntry:
    """A single forensic entry in the audit trail."""
    request_id: str
    timestamp: float
    layer: str
    decision: str
    details: dict[str, Any]
    color_code: str   # SOC dashboard color: GREEN/YELLOW/ORANGE/RED

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "layer": self.layer,
            "decision": self.decision,
            "details": self.details,
            "color_code": self.color_code,
        }


def generate_request_id(request: dict[str, Any]) -> str:
    """Generate a deterministic request ID for correlation."""
    content = json.dumps(request, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def color_for_risk(risk_score: float) -> str:
    """Map risk score to SOC dashboard color code."""
    if risk_score >= 0.8:
        return "RED"
    elif risk_score >= 0.5:
        return "ORANGE"
    elif risk_score >= 0.3:
        return "YELLOW"
    return "GREEN"


def build_audit_trail(
    request: dict[str, Any],
    forensic_trail: list[dict[str, Any]],
    final_decision: str,
) -> list[AuditEntry]:
    """Build a structured audit trail from the forensic stamps.

    Args:
        request:        Original agent request.
        forensic_trail: List of per-layer forensic dicts from ValidationResult.
        final_decision: Final ALLOW/BLOCK/ESCALATE decision.

    Returns:
        List of AuditEntry objects ready for SOC dashboard ingestion.
    """
    request_id = generate_request_id(request)
    entries: list[AuditEntry] = []

    for stamp in forensic_trail:
        layer = stamp.get("layer", "unknown")
        risk = stamp.get("risk_score", 0.0)
        decision = stamp.get("decision", stamp.get("permitted", "N/A"))

        if isinstance(decision, bool):
            decision = "PERMIT" if decision else "DENY"

        entries.append(AuditEntry(
            request_id=request_id,
            timestamp=stamp.get("timestamp", time.time()),
            layer=layer,
            decision=str(decision),
            details=stamp,
            color_code=color_for_risk(risk if isinstance(risk, float) else 0.0),
        ))

    # Final summary entry
    entries.append(AuditEntry(
        request_id=request_id,
        timestamp=time.time(),
        layer="pipeline",
        decision=final_decision,
        details={"layers_count": len(forensic_trail)},
        color_code=color_for_risk(1.0 if final_decision == "BLOCK" else 0.0),
    ))

    return entries


def format_audit_log(entries: list[AuditEntry]) -> str:
    """Format audit trail as human-readable log lines."""
    lines = []
    for e in entries:
        lines.append(
            f"[{e.color_code:>6}] {e.layer:>10} | {e.decision:>8} | {e.request_id}"
        )
    return "\n".join(lines)
