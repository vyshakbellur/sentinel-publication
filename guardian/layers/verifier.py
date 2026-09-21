"""
Guardian Layer 3: Permission Verifier

Implements Intent-Based Access Control (IBAC) — Principle 3: Independent
Verification. The Verifier and the LLM share zero context; the decision
to execute is separated from the request generation.

Checks:
  1. User has permission for the classified intent
  2. Action target is within the user's scope
  3. Statistical anomaly detection (cross-check against user history)
  4. Cooldown enforcement for high-risk actions
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from guardian.layers.classifier import IntentClassification, IntentType

# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VerificationResult:
    """Result from the Verifier layer with forensic metadata."""
    permitted: bool
    checks_passed: list[str]
    checks_failed: list[str]
    latency_ms: float
    metadata: dict[str, Any]

    requires_human_approval: bool = False

    @property
    def denied(self) -> bool:
        return not self.permitted


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class VerifierConfig:
    """Permission verification thresholds."""

    # ── Default user permissions ─────────────────────────────────────────
    default_permissions: frozenset[str] = frozenset({
        "READ",   # All users can read by default
    })

    # ── High-risk action cooldown (seconds) ──────────────────────────────
    trade_cooldown_seconds: float = 30.0
    admin_cooldown_seconds: float = 60.0

    # ── Statistical thresholds ───────────────────────────────────────────
    max_daily_trades: int = 50
    max_daily_admin_actions: int = 10
    anomaly_z_threshold: float = 2.5   # Flag if action rate > 2.5σ above mean


DEFAULT_VERIFIER_CONFIG = VerifierConfig()


# ─────────────────────────────────────────────────────────────────────────────
# Verification Checks
# ─────────────────────────────────────────────────────────────────────────────

def _check_permission(
    classification: IntentClassification,
    user_permissions: dict[str, Any],
    cfg: VerifierConfig,
) -> tuple[str, bool]:
    """Check 1: Does the user have permission for this intent?"""
    allowed_intents = user_permissions.get(
        "allowed_intents",
        set(cfg.default_permissions),
    )
    if isinstance(allowed_intents, list):
        allowed_intents = set(allowed_intents)
    if not isinstance(allowed_intents, (set, frozenset, tuple)):
        return ("permission:malformed_fail_closed", False)

    intent_name = classification.intent.value
    passed = intent_name in allowed_intents

    return (
        f"permission:{intent_name}",
        passed,
    )


def _check_scope(
    request: dict[str, Any],
    user_permissions: dict[str, Any],
) -> tuple[str, bool]:
    """Check 2: Is the action target within the user's scope? (Fail-closed)"""
    target = request.get("target", request.get("tool_name", ""))
    allowed_scope = user_permissions.get("allowed_scope", set())

    if not isinstance(target, str):
        return ("scope:malformed_target_fail_closed", False)

    # FAIL-CLOSED: If no scope is defined, deny by default.
    if not allowed_scope:
        return ("scope:undefined_fail_closed", False)

    if isinstance(allowed_scope, list):
        allowed_scope = set(allowed_scope)
    if not isinstance(allowed_scope, (set, frozenset, tuple)):
        return ("scope:malformed_fail_closed", False)

    # Check if target is in scope or if user has wildcard access
    if "*" in allowed_scope or target in allowed_scope:
        return (f"scope:{target}", True)

    # Check prefix matches (e.g., "portfolio.*" allows "portfolio.balances")
    for scope in allowed_scope:
        if not isinstance(scope, str):
            continue
        # "portfolio.*" authorizes "portfolio.balances", not the look-alike
        # target "portfolioevil".
        if scope.endswith(".*") and target.startswith(scope[:-1]):
            return (f"scope:{target}⊆{scope}", True)

    return (f"scope:{target}_denied", False)


def _check_request_schema(request: dict[str, Any]) -> tuple[str, bool]:
    """Validate the framework-level proposal envelope.

    This is intentionally not a tool-specific argument schema. Production
    deployments must additionally validate parameters against a trusted tool
    manifest at the broker boundary.
    """
    if not isinstance(request, dict):
        return ("schema:request_not_object", False)

    required_strings = {
        "tool_name": request.get("tool_name"),
        "operation": request.get("operation"),
    }
    for field_name, value in required_strings.items():
        if not isinstance(value, str) or not value.strip():
            return (f"schema:{field_name}_invalid", False)

    parameters = request.get("parameters", {})
    if not isinstance(parameters, dict):
        return ("schema:parameters_not_object", False)

    source = request.get("source")
    destination = request.get("destination")
    if not isinstance(source, dict):
        return ("schema:source_not_object", False)
    if not isinstance(destination, dict):
        return ("schema:destination_not_object", False)

    data_class = source.get("classification")
    trust_domain = destination.get("trust_domain")
    if not isinstance(data_class, str) or not data_class.strip():
        return ("schema:source_classification_invalid", False)
    if not isinstance(trust_domain, str) or not trust_domain.strip():
        return ("schema:destination_trust_invalid", False)

    for field_name in ("inputs", "outputs"):
        values = request.get(field_name, [])
        if not isinstance(values, list) or not all(
            isinstance(item, str) and item for item in values
        ):
            return (f"schema:{field_name}_invalid", False)

    return ("schema:envelope_valid", True)


def _is_finite_number(value: Any, *, minimum: float = 0.0) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
        and value >= minimum
    )


def _check_data_flow(
    request: dict[str, Any],
    classification: IntentClassification,
    user_permissions: dict[str, Any],
) -> tuple[str, bool]:
    """Check 2b: Consequence-aware Data flow and parameter validation."""
    # 1. Canonical structured action checking
    dest = request.get("destination", {})
    source = request.get("source", {})

    trust_domain = dest.get("trust_domain", "").lower() if isinstance(dest, dict) else ""
    data_class = source.get("classification", "").lower() if isinstance(source, dict) else ""

    # Block external transmission of confidential/secret data
    if trust_domain.startswith("external"):
        if data_class in ("secret", "confidential"):
            return (f"data_flow_denied:{data_class}_to_{trust_domain}", False)

    # 2. Legacy parameter checking (backward compatibility)
    params = request.get("parameters", {})
    if isinstance(params, dict):
        # Only apply network-domain policy to an actual locator. A logical
        # resource name such as "internal_dashboard" is scope, not a hostname.
        dest_param = params.get("url")
        if dest_param is None:
            candidate = params.get("destination")
            if isinstance(candidate, str) and (
                "://" in candidate or candidate.startswith("//") or "." in candidate
            ):
                dest_param = candidate

        if dest_param:
            allowed_domains = user_permissions.get("allowed_domains", [])
            if allowed_domains:
                if not _destination_is_allowed(str(dest_param), allowed_domains):
                    return (f"param_dest_denied:{dest_param}", False)
            else:
                return ("param_dest_denied:no_allowed_domains", False)

    return ("data_flow:validated", True)


def _canonical_hostname(value: str) -> str | None:
    """Return a normalized hostname without trusting URL substrings."""
    candidate = value.strip()
    if not candidate:
        return None

    parsed = urlsplit(candidate if "://" in candidate else f"//{candidate}")
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        return None
    if parsed.username or parsed.password:
        return None

    hostname = parsed.hostname
    if not hostname:
        return None

    try:
        return hostname.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError:
        return None


def _destination_is_allowed(destination: str, allowed_domains: Any) -> bool:
    """Match exact hosts or real subdomains; reject look-alike substrings."""
    destination_host = _canonical_hostname(destination)
    if destination_host is None:
        return False

    if isinstance(allowed_domains, str):
        allowed_domains = [allowed_domains]

    for entry in allowed_domains:
        if not isinstance(entry, str):
            continue
        allowed_host = _canonical_hostname(entry)
        if allowed_host and (
            destination_host == allowed_host
            or destination_host.endswith(f".{allowed_host}")
        ):
            return True
    return False


def _check_rate_limit(
    classification: IntentClassification,
    user_permissions: dict[str, Any],
    cfg: VerifierConfig,
) -> tuple[str, bool]:
    """Check 3: Has the user exceeded daily action limits?"""
    history = user_permissions.get("action_history", {})
    if not isinstance(history, dict):
        return ("rate_limit:malformed_history_fail_closed", False)

    if classification.intent == IntentType.TRADE:
        daily_count = history.get("daily_trades", 0)
        if not _is_finite_number(daily_count):
            return ("rate_limit:malformed_daily_trades_fail_closed", False)
        if daily_count >= cfg.max_daily_trades:
            return (f"rate_limit:trades={daily_count}/{cfg.max_daily_trades}", False)
    elif classification.intent == IntentType.ADMIN:
        daily_count = history.get("daily_admin_actions", 0)
        if not _is_finite_number(daily_count):
            return ("rate_limit:malformed_daily_admin_actions_fail_closed", False)
        if daily_count >= cfg.max_daily_admin_actions:
            return (f"rate_limit:admin={daily_count}/{cfg.max_daily_admin_actions}", False)

    return ("rate_limit:within_bounds", True)


def _check_cooldown(
    classification: IntentClassification,
    user_permissions: dict[str, Any],
    cfg: VerifierConfig,
) -> tuple[str, bool]:
    """Check 4: Is the user in a cooldown period for high-risk actions?"""
    history = user_permissions.get("action_history", {})
    if not isinstance(history, dict):
        return ("cooldown:malformed_history_fail_closed", False)
    last_action_time = history.get("last_high_risk_action", 0)
    if not _is_finite_number(last_action_time):
        return ("cooldown:malformed_last_action_time_fail_closed", False)
    now = time.time()
    elapsed = now - last_action_time

    if classification.intent == IntentType.TRADE:
        if elapsed < cfg.trade_cooldown_seconds:
            remaining = round(cfg.trade_cooldown_seconds - elapsed, 1)
            return (f"cooldown:trade_{remaining}s_remaining", False)
    elif classification.intent == IntentType.ADMIN:
        if elapsed < cfg.admin_cooldown_seconds:
            remaining = round(cfg.admin_cooldown_seconds - elapsed, 1)
            return (f"cooldown:admin_{remaining}s_remaining", False)

    return ("cooldown:clear", True)


def _check_statistical_anomaly(
    classification: IntentClassification,
    user_permissions: dict[str, Any],
    cfg: VerifierConfig,
) -> tuple[str, bool]:
    """Check 5: Is this action statistically anomalous for this user?"""
    history = user_permissions.get("action_history", {})
    if not isinstance(history, dict):
        return ("anomaly:malformed_history_fail_closed", False)
    avg_daily = history.get("avg_daily_actions", 10)
    std_daily = history.get("std_daily_actions", 3)
    today_count = history.get("today_action_count", 0)

    if not all(
        _is_finite_number(value)
        for value in (avg_daily, std_daily, today_count)
    ):
        return ("anomaly:malformed_statistics_fail_closed", False)

    if std_daily > 0:
        z_score = (today_count - avg_daily) / std_daily
        if z_score > cfg.anomaly_z_threshold:
            return (f"anomaly:z={round(z_score, 2)}", False)

    return ("anomaly:normal", True)


# ─────────────────────────────────────────────────────────────────────────────
# Verification Registry
# ─────────────────────────────────────────────────────────────────────────────

_VERIFICATION_CHECKS = [
    "permission",
    "scope",
    "parameters",
    "rate_limit",
    "cooldown",
    "statistical_anomaly",
]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def verify_baseline_permission(
    request: dict[str, Any],
    classification: IntentClassification,
    user_permissions: dict[str, Any] | None = None,
    config: VerifierConfig | None = None,
) -> VerificationResult:
    """Run mandatory low-cost authorization checks for every tool proposal.

    Progressive validation may skip expensive contextual verification, but it
    must never skip permission, scope, or data-flow enforcement.
    """
    cfg = config or DEFAULT_VERIFIER_CONFIG
    perms = (
        user_permissions
        if isinstance(user_permissions, dict)
        else {"allowed_intents": set(cfg.default_permissions)}
    )
    start = time.perf_counter()

    checks = [
        _check_request_schema(request),
        _check_permission(classification, perms, cfg),
        _check_scope(request, perms),
        _check_data_flow(request, classification, perms),
    ]
    passed = [name for name, ok in checks if ok]
    failed = [name for name, ok in checks if not ok]

    return VerificationResult(
        permitted=not failed,
        checks_passed=passed,
        checks_failed=failed,
        latency_ms=round((time.perf_counter() - start) * 1000, 2),
        requires_human_approval=False,
        metadata={
            "layer": "policy",
            "intent": classification.intent.value,
            "risk_tier": classification.risk_tier.value,
            "total_checks": len(checks),
            "timestamp": time.time(),
        },
    )

def verify_permission(
    request: dict[str, Any],
    classification: IntentClassification,
    user_permissions: dict[str, Any] | None = None,
    config: VerifierConfig | None = None,
) -> VerificationResult:
    """Verify if the classified request is permitted for the user.

    Implements IBAC (Intent-Based Access Control). The Verifier runs
    independently of the LLM — Principle 3: Independent Verification.

    Args:
        request:          Original agent request.
        classification:   Intent classification from Layer 2.
        user_permissions:  User's permission profile (allowed intents, scope, history).
        config:           Verifier configuration.

    Returns:
        VerificationResult with pass/fail status and forensic trail.
    """
    cfg = config or DEFAULT_VERIFIER_CONFIG
    perms = (
        user_permissions
        if isinstance(user_permissions, dict)
        else {"allowed_intents": set(cfg.default_permissions)}
    )
    start = time.perf_counter()

    passed: list[str] = []
    failed: list[str] = []

    # Run all checks
    checks = [
        _check_request_schema(request),
        _check_permission(classification, perms, cfg),
        _check_scope(request, perms),
        _check_data_flow(request, classification, perms),
        _check_rate_limit(classification, perms, cfg),
        _check_cooldown(classification, perms, cfg),
        _check_statistical_anomaly(classification, perms, cfg),
    ]

    for check_name, check_passed in checks:
        if check_passed:
            passed.append(check_name)
        else:
            failed.append(check_name)

    # 5. Check if action requires human approval
    requires_human_approval = False
    if classification.intent in (IntentType.ADMIN, IntentType.EXECUTION):
        requires_human_approval = True

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return VerificationResult(
        permitted=len(failed) == 0,
        checks_passed=passed,
        checks_failed=failed,
        latency_ms=elapsed_ms,
        requires_human_approval=requires_human_approval,
        metadata={
            "layer": "verifier",
            "intent": classification.intent.value,
            "risk_tier": classification.risk_tier.value,
            "total_checks": len(checks),
            "timestamp": time.time(),
        },
    )
