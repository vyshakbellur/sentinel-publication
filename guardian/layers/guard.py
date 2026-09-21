"""
Guardian Layer 1: Deterministic Guard

The first line of defense. Pure regex + dictionary lookups with ZERO LLM
involvement. Enforces Principle 1 ("Enforce Outside the Model").

Screens every incoming agent request for:
  1. Known prompt injection patterns (regex)
  2. Blocklisted tool calls
  3. Rate limit violations
  4. Payload size anomalies
  5. Suspicious parameter patterns

Returns ALLOW, BLOCK, or ESCALATE with a forensic stamp.
"""

from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

class GuardDecision(Enum):
    """Outcome of the deterministic guard screening."""
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"

class EscalationReason(Enum):
    """Specific reasons for escalation."""
    RISK_ROUTING = "RISK_ROUTING"
    INJECTION = "INJECTION"
    RATE_ANOMALY = "RATE_ANOMALY"
    POLICY_REVIEW = "POLICY_REVIEW"


@dataclass
class GuardResult:
    """Result from the Guard layer with forensic metadata."""
    decision: GuardDecision
    triggered_rules: list[str]
    risk_score: float          # 0.0 = safe, 1.0 = maximum threat
    risk_tier_floor: str       # Monotonic risk floor (LOW, MEDIUM, HIGH, CRITICAL)
    latency_ms: float          # Screening time in milliseconds
    metadata: dict[str, Any]   # Forensic stamp

    requires_deep_verification: bool = False
    requires_human_review: bool = False
    escalation_reasons: list[EscalationReason] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return self.decision == GuardDecision.BLOCK


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GuardConfig:
    """All guard thresholds and patterns, centralized for tuning."""

    # ── Injection detection ──────────────────────────────────────────────
    injection_patterns: tuple[str, ...] = (
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"system\s*prompt\s*[:=]",
        r"forget\s+(all\s+)?(your\s+)?instructions",
        r"do\s+not\s+follow\s+(the\s+)?(above|previous)",
        r"override\s+(system|safety)\s+(prompt|instructions|settings)",
        r"act\s+as\s+(if|though)\s+you\s+(are|were)\s+(a|an)\s+unrestricted",
        r"jailbreak",
        r"DAN\s*mode",
        r"\bexfiltrate\b",
        r"reveal\s+(your|the)\s+(system|hidden)\s+prompt",
        r"output\s+(your|the)\s+(initial|system)\s+instructions",
    )

    # ── Blocklisted tools ────────────────────────────────────────────────
    blocked_tools: frozenset[str] = frozenset({
        "rm_rf", "drop_table", "drop_database", "truncate_table",
        "delete_all_records", "format_disk", "shutdown_system",
        "disable_firewall", "revoke_all_permissions",
        "transfer_funds_unlimited", "execute_arbitrary_code",
        "download_external_binary", "modify_system_prompt",
    })

    # ── Suspicious parameter patterns ────────────────────────────────────
    suspicious_param_patterns: tuple[str, ...] = (
        r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER)\s+",    # SQL injection
        r"<script[\s>]",                                # XSS
        r"\.\./\.\./",                                  # Path traversal
        r"\\x[0-9a-fA-F]{2}",                          # Hex-encoded payloads
        r"eval\s*\(",                                   # Code injection
        r"__import__\s*\(",                             # Python injection
    )

    # ── Thresholds ───────────────────────────────────────────────────────
    max_payload_bytes: int = 50_000           # 50 KB payload limit
    max_tool_args: int = 20                   # Max number of tool arguments
    escalation_risk_threshold: float = 0.4    # Above this → ESCALATE
    block_risk_threshold: float = 0.7         # Above this → BLOCK

    # ── Weights for risk score composition ───────────────────────────────
    w_injection: float = 0.40
    w_blocked_tool: float = 0.35
    w_suspicious_params: float = 0.15
    w_payload_anomaly: float = 0.10


DEFAULT_GUARD_CONFIG = GuardConfig()


# ─────────────────────────────────────────────────────────────────────────────
# Check Functions — each returns (rule_name, score) or None
# ─────────────────────────────────────────────────────────────────────────────

def _check_injection(
    request: dict[str, Any], cfg: GuardConfig
) -> tuple[str, float] | None:
    """Check 1: Scan for prompt injection patterns in all string fields."""
    text_fields = []

    # Collect all string content from the request
    for key, val in request.items():
        if isinstance(val, str):
            text_fields.append(val)
        elif isinstance(val, dict):
            for v in val.values():
                if isinstance(v, str):
                    text_fields.append(v)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    text_fields.append(item)

    combined = " ".join(text_fields).lower()

    matches = []
    for pattern in cfg.injection_patterns:
        if re.search(pattern, combined, re.IGNORECASE):
            matches.append(pattern)

    if not matches:
        return None

    # More matches = higher confidence of injection
    score = min(1.0, 0.5 + len(matches) * 0.15)
    return (f"injection:{len(matches)}_patterns_matched", score)


def _check_blocked_tool(
    request: dict[str, Any], cfg: GuardConfig
) -> tuple[str, float] | None:
    """Check 2: Is the requested tool in the blocklist?"""
    raw_tool = request.get("tool_name", "")
    if not isinstance(raw_tool, str):
        return ("malformed_tool_name", 1.0)
    tool = raw_tool.lower().strip()
    if not tool:
        return None

    if tool in cfg.blocked_tools:
        return (f"blocked_tool:{tool}", 1.0)

    # Partial match for obfuscation attempts (e.g., "rm__rf", "dr0p_table")
    normalized = re.sub(r"[^a-z]", "", tool)
    for blocked in cfg.blocked_tools:
        blocked_norm = re.sub(r"[^a-z]", "", blocked)
        if blocked_norm and normalized == blocked_norm:
            return (f"blocked_tool_obfuscated:{tool}→{blocked}", 0.9)

    return None


def _check_suspicious_params(
    request: dict[str, Any], cfg: GuardConfig
) -> tuple[str, float] | None:
    """Check 3: Scan tool parameters for injection patterns."""
    params = request.get("parameters", {})
    if not isinstance(params, dict):
        return None

    param_text = " ".join(str(v) for v in params.values())

    matches = []
    for pattern in cfg.suspicious_param_patterns:
        if re.search(pattern, param_text, re.IGNORECASE):
            matches.append(pattern)

    if not matches:
        return None

    score = min(1.0, 0.4 + len(matches) * 0.2)
    return (f"suspicious_params:{len(matches)}_patterns", score)


def _check_payload_anomaly(
    request: dict[str, Any], cfg: GuardConfig
) -> tuple[str, float] | None:
    """Check 4: Detect oversized payloads or excessive arguments."""
    import json
    try:
        payload_size = len(json.dumps(request, default=str))
    except (TypeError, ValueError, RecursionError):
        return ("malformed_payload:not_serializable", 1.0)

    triggered = []
    score = 0.0

    if payload_size > cfg.max_payload_bytes:
        ratio = payload_size / cfg.max_payload_bytes
        score = min(1.0, (ratio - 1.0) * 0.3)
        triggered.append(f"payload_{payload_size}B")

    params = request.get("parameters", {})
    if isinstance(params, dict) and len(params) > cfg.max_tool_args:
        arg_score = min(1.0, (len(params) - cfg.max_tool_args) / 20)
        score = max(score, arg_score)
        triggered.append(f"args_{len(params)}")

    if not triggered:
        return None

    return (f"payload_anomaly:{'+'.join(triggered)}", score)


def _check_rate_context(
    request: dict[str, Any], cfg: GuardConfig
) -> tuple[str, float] | None:
    """Check 5: Flag requests with anomalous rate context metadata."""
    rate_ctx = request.get("_rate_context", {})
    if not rate_ctx:
        return None
    if not isinstance(rate_ctx, dict):
        return ("malformed_rate_context", 1.0)

    requests_per_min = rate_ctx.get("requests_per_minute", 0)
    writes_per_min = rate_ctx.get("writes_per_minute", 0)

    numeric_values = (requests_per_min, writes_per_min)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
        for value in numeric_values
    ):
        return ("malformed_rate_context", 1.0)

    if requests_per_min > 200:  # Extreme burst
        return ("rate_burst", min(1.0, requests_per_min / 500))

    if writes_per_min > 20:  # Write storm
        return ("write_storm", min(1.0, writes_per_min / 50))

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Check Registry
# ─────────────────────────────────────────────────────────────────────────────

_GUARD_CHECKS = [
    ("injection", _check_injection),
    ("blocked_tool", _check_blocked_tool),
    ("suspicious_params", _check_suspicious_params),
    ("payload_anomaly", _check_payload_anomaly),
    ("rate_context", _check_rate_context),
]


# ─────────────────────────────────────────────────────────────────────────────
# Risk Matrix and Monotonic Floor
# ─────────────────────────────────────────────────────────────────────────────

_RISK_MATRIX_PATH = Path(__file__).parent.parent / "config" / "risk_matrix.json"
_RISK_MATRIX_CACHE: dict[str, Any] = {}

def _get_risk_matrix() -> dict[str, Any]:
    global _RISK_MATRIX_CACHE
    if not _RISK_MATRIX_CACHE and _RISK_MATRIX_PATH.exists():
        _RISK_MATRIX_CACHE = json.loads(_RISK_MATRIX_PATH.read_text())
    return _RISK_MATRIX_CACHE

def _calculate_risk_floor(request: dict[str, Any]) -> str:
    """Calculate the deterministic, non-bypassable risk floor based on argument-level consequence."""
    matrix = _get_risk_matrix()
    if not matrix:
        return "CRITICAL"  # FAIL CLOSED if matrix is missing

    # Extract structured action properties
    # FAIL CLOSED: Missing or malformed attributes default to UNKNOWN which maps to high risk.
    operation = request.get("operation", "unknown")
    operation = operation.lower() if isinstance(operation, str) else "unknown"

    source = request.get("source", {})
    source_class = source.get("classification", "unknown") if isinstance(source, dict) else "unknown"
    source_class = source_class.lower() if isinstance(source_class, str) else "unknown"

    dest = request.get("destination", {})
    dest_trust = dest.get("trust_domain", "unknown") if isinstance(dest, dict) else "unknown"
    dest_trust = dest_trust.lower() if isinstance(dest_trust, str) else "unknown"

    # Get raw values (defaulting to CRITICAL if missing)
    op_data = matrix.get("operations", {}).get(operation, {"capability_floor": "CRITICAL", "irreversibility": "CRITICAL"})
    cap_floor_str = op_data.get("capability_floor", "CRITICAL")
    irrev_str = op_data.get("irreversibility", "CRITICAL")

    # 4 is the maximum value for sensitivity and trust in the matrix
    sens_val = matrix.get("data_sensitivity", {}).get(source_class, 4)
    trust_val = matrix.get("destination_trust", {}).get(dest_trust, 4)

    # Convert enum strings to thresholds
    thresholds = matrix.get("risk_thresholds", {"LOW": 4, "MEDIUM": 8, "HIGH": 12, "CRITICAL": 16})
    cap_val = thresholds.get(cap_floor_str, 4)
    irrev_val = thresholds.get(irrev_str, 4)

    # Monotonic formula
    cumulative = sens_val * trust_val
    floor_val = max(cap_val, cumulative, irrev_val)

    # Map back to string tier
    if floor_val >= thresholds.get("CRITICAL", 16):
        return "CRITICAL"
    if floor_val >= thresholds.get("HIGH", 12):
        return "HIGH"
    if floor_val >= thresholds.get("MEDIUM", 8):
        return "MEDIUM"
    return "LOW"

# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def screen_request(
    request: dict[str, Any],
    config: GuardConfig | None = None,
) -> GuardResult:
    """Screen an incoming agent request through deterministic checks.

    This is the Guard layer — Principle 1: Enforce Outside the Model.
    All checks are regex/dictionary-based. Zero LLM involvement.

    Args:
        request: Agent request dict with keys like 'tool_name', 'parameters',
                 'prompt', 'user_id', etc.
        config:  Guard configuration. Uses DEFAULT_GUARD_CONFIG if None.

    Returns:
        GuardResult with decision (ALLOW/BLOCK/ESCALATE), triggered rules,
        composite risk score, latency, and forensic metadata.
    """
    cfg = config or DEFAULT_GUARD_CONFIG
    start = time.perf_counter()

    if not isinstance(request, dict):
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return GuardResult(
            decision=GuardDecision.BLOCK,
            triggered_rules=["malformed_request:not_object"],
            risk_score=1.0,
            risk_tier_floor="CRITICAL",
            latency_ms=elapsed_ms,
            requires_deep_verification=True,
            requires_human_review=False,
            escalation_reasons=[],
            metadata={
                "layer": "guard",
                "checks_run": 1,
                "rules_triggered": 1,
                "timestamp": time.time(),
            },
        )

    triggered_rules: list[str] = []
    max_score = 0.0

    # Run each check
    for check_name, check_fn in _GUARD_CHECKS:
        try:
            result = check_fn(request, cfg)
        except (TypeError, ValueError, RecursionError):
            # A malformed proposal must not turn the policy boundary into an
            # availability or authorization bypass. Preserve the failing
            # check name in the forensic record and fail closed.
            result = (f"check_error:{check_name}", 1.0)
        if result is not None:
            rule_name, score = result
            triggered_rules.append(rule_name)
            max_score = max(max_score, score)

    # Determine decision
    risk_score = round(min(1.0, max_score), 3)

    requires_human_review = False
    escalation_reasons = []

    if risk_score >= cfg.block_risk_threshold:
        decision = GuardDecision.BLOCK
    elif risk_score >= cfg.escalation_risk_threshold:
        decision = GuardDecision.ESCALATE
        requires_human_review = True
        if any(r.startswith("injection") for r in triggered_rules):
            escalation_reasons.append(EscalationReason.INJECTION)
        if any(r.startswith("rate") for r in triggered_rules):
            escalation_reasons.append(EscalationReason.RATE_ANOMALY)
        if not escalation_reasons:
            escalation_reasons.append(EscalationReason.POLICY_REVIEW)
    else:
        decision = GuardDecision.ALLOW

    # Calculate deterministic risk floor
    risk_tier_floor = _calculate_risk_floor(request)

    requires_deep_verification = risk_tier_floor in ("HIGH", "CRITICAL")

    if requires_deep_verification and decision == GuardDecision.ALLOW:
        escalation_reasons.append(EscalationReason.RISK_ROUTING)

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return GuardResult(
        decision=decision,
        triggered_rules=triggered_rules,
        risk_score=risk_score,
        risk_tier_floor=risk_tier_floor,
        latency_ms=elapsed_ms,
        requires_deep_verification=requires_deep_verification,
        requires_human_review=requires_human_review,
        escalation_reasons=escalation_reasons,
        metadata={
            "layer": "guard",
            "checks_run": len(_GUARD_CHECKS),
            "rules_triggered": len(triggered_rules),
            "timestamp": time.time(),
        },
    )
