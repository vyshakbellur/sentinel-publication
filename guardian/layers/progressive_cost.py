"""
Guardian Progressive Cost Orchestrator

Implements Principle 2 ("Progressive Cost") and Principle 5
("Cost of Verification ∝ Risk of Action").

Validation depth scales with risk:
  ALL risk:     Guard + Classifier + mandatory local authorization
  LOW risk:     Stop after mandatory local authorization
  MEDIUM+:      Add contextual Verifier checks

Semantic/DLP services are extension points, not implemented in this module.

This orchestrator runs the 3-layer pipeline and collects the composite
forensic trail (Principle 4: Leave a Mark Everywhere).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from guardian.layers.classifier import (
    ClassifierConfig,
    IntentClassification,
    RiskTier,
    classify_intent,
)
from guardian.layers.guard import (
    GuardConfig,
    GuardDecision,
    GuardResult,
    screen_request,
)
from guardian.layers.verifier import (
    VerificationResult,
    VerifierConfig,
    verify_baseline_permission,
    verify_permission,
)

# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    """Complete validation result from the progressive cost pipeline."""
    decision: str               # ALLOW, BLOCK, ESCALATE
    risk_tier: str              # LOW, MEDIUM, HIGH, CRITICAL
    layers_invoked: list[str]   # Which layers ran
    total_checks: int           # Total checks performed
    total_latency_ms: float     # End-to-end latency
    guard_result: GuardResult | None
    classification: IntentClassification | None
    verification: VerificationResult | None
    forensic_trail: list[dict[str, Any]]  # Complete audit trail

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"

    @property
    def blocked(self) -> bool:
        return self.decision == "BLOCK"


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GuardianConfig:
    """Top-level configuration for the full Guardian pipeline."""
    guard: GuardConfig = GuardConfig()
    classifier: ClassifierConfig = ClassifierConfig()
    verifier: VerifierConfig = VerifierConfig()

    # ── Progressive cost mode ────────────────────────────────────────────
    # "progressive": Only run layers needed for the risk tier
    # "full":        Always run all layers (baseline comparison)
    mode: str = "progressive"

    # ── Classification method ────────────────────────────────────────────
    classify_method: str = "rule"   # "rule" or "llm"


DEFAULT_GUARDIAN_CONFIG = GuardianConfig()


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def _validate_request_core(
    request: dict[str, Any],
    user_permissions: dict[str, Any] | None = None,
    config: GuardianConfig | None = None,
    *,
    classification_override: IntentClassification | None = None,
) -> ValidationResult:
    """Run the full Guardian pipeline with progressive cost validation.

    Implements the core Guardian paradigm: validation depth scales with risk.

    Args:
        request:          Agent request dict.
        user_permissions: User permission profile (for Verifier layer).
        config:           Full Guardian configuration.

    Returns:
        ValidationResult with decision, forensic trail, and per-layer results.
    """
    cfg = config or DEFAULT_GUARDIAN_CONFIG
    if cfg.mode not in {"progressive", "full"}:
        raise ValueError(
            f"Unsupported Guardian mode {cfg.mode!r}; expected 'progressive' or 'full'"
        )
    start = time.perf_counter()

    layers_invoked: list[str] = []
    forensic_trail: list[dict[str, Any]] = []
    total_checks = 0

    guard_result: GuardResult | None = None
    classification: IntentClassification | None = None
    verification: VerificationResult | None = None

    # ── Layer 1: Guard (ALWAYS runs) ─────────────────────────────────────
    guard_result = screen_request(request, cfg.guard)
    layers_invoked.append("guard")
    total_checks += guard_result.metadata.get("checks_run", 5)
    forensic_trail.append({
        "layer": "guard",
        "decision": guard_result.decision.value,
        "risk_score": guard_result.risk_score,
        "rules_triggered": guard_result.triggered_rules,
        "latency_ms": guard_result.latency_ms,
    })

    # If Guard blocks, stop immediately
    if guard_result.decision == GuardDecision.BLOCK:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return ValidationResult(
            decision="BLOCK",
            risk_tier="BLOCKED_AT_GUARD",
            layers_invoked=layers_invoked,
            total_checks=total_checks,
            total_latency_ms=elapsed,
            guard_result=guard_result,
            classification=None,
            verification=None,
            forensic_trail=forensic_trail,
        )

    # ── Layer 2: Classifier ──────────────────────────────────────────────
    # In progressive mode, classify to determine how deep to go
    classification = classification_override or classify_intent(
        request, cfg.classify_method, cfg.classifier
    )
    original_classifier_tier = classification.risk_tier.value

    # ENFORCE MONOTONIC RISK FLOOR
    # The semantic classifier can raise the risk, but can never lower it below the deterministic Guard floor.
    tier_weights = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    floor_weight = tier_weights.get(guard_result.risk_tier_floor, 1)
    class_weight = tier_weights.get(classification.risk_tier.value, 1)

    effective_risk_tier_val = max(floor_weight, class_weight)

    # Map back to enum
    effective_risk_tier = RiskTier.LOW
    for tier, weight in tier_weights.items():
        if weight == effective_risk_tier_val:
            effective_risk_tier = RiskTier(tier)
            break

    # Override classification tier with the monotonic floor if necessary
    if effective_risk_tier_val > class_weight:
        classification.risk_tier = effective_risk_tier
        classification.reasoning = f"Overridden by Guard monotonic floor ({guard_result.risk_tier_floor})"

    layers_invoked.append("classifier")
    total_checks += 2  # tool name check + content analysis
    forensic_trail.append({
        "layer": "classifier",
        "intent": classification.intent.value,
        "original_classifier_tier": original_classifier_tier,
        "effective_risk_tier": classification.risk_tier.value,
        "confidence": classification.confidence,
        "method": classification.method,
        "reasoning": classification.reasoning,
        "latency_ms": classification.latency_ms,
    })

    # Mandatory authorization is not optional. Progressive mode may skip
    # expensive contextual verification, but never permission, scope, or
    # consequence-aware data-flow enforcement.
    baseline_verification = verify_baseline_permission(
        request, classification, user_permissions, cfg.verifier
    )
    layers_invoked.append("policy")
    total_checks += baseline_verification.metadata.get("total_checks", 4)
    forensic_trail.append({
        "layer": "policy",
        "permitted": baseline_verification.permitted,
        "checks_passed": baseline_verification.checks_passed,
        "checks_failed": baseline_verification.checks_failed,
        "latency_ms": baseline_verification.latency_ms,
    })

    if baseline_verification.denied:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return ValidationResult(
            decision="BLOCK",
            risk_tier=classification.risk_tier.value,
            layers_invoked=layers_invoked,
            total_checks=total_checks,
            total_latency_ms=elapsed,
            guard_result=guard_result,
            classification=classification,
            verification=baseline_verification,
            forensic_trail=forensic_trail,
        )

    # In progressive mode, LOW risk stops after mandatory local policy.
    if (cfg.mode == "progressive"
            and classification.risk_tier == RiskTier.LOW
            and guard_result.decision == GuardDecision.ALLOW):
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return ValidationResult(
            decision="ALLOW",
            risk_tier=classification.risk_tier.value,
            layers_invoked=layers_invoked,
            total_checks=total_checks,
            total_latency_ms=elapsed,
            guard_result=guard_result,
            classification=classification,
            verification=baseline_verification,
            forensic_trail=forensic_trail,
        )

    # ── Layer 3: Verifier (MEDIUM, HIGH, CRITICAL) ───────────────────────
    verification = verify_permission(
        request, classification, user_permissions, cfg.verifier
    )
    layers_invoked.append("verifier")
    total_checks += verification.metadata.get("total_checks", 5)
    forensic_trail.append({
        "layer": "verifier",
        "permitted": verification.permitted,
        "checks_passed": verification.checks_passed,
        "checks_failed": verification.checks_failed,
        "latency_ms": verification.latency_ms,
    })

    # Determine final decision
    if guard_result.blocked:
        decision = "BLOCK"
    elif verification.denied:
        decision = "BLOCK"
    elif guard_result.requires_human_review:
        decision = "ESCALATE"
    elif verification.requires_human_approval:
        decision = "ESCALATE"
    else:
        decision = "ALLOW"

    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return ValidationResult(
        decision=decision,
        risk_tier=classification.risk_tier.value,
        layers_invoked=layers_invoked,
        total_checks=total_checks,
        total_latency_ms=elapsed,
        guard_result=guard_result,
        classification=classification,
        verification=verification,
        forensic_trail=forensic_trail,
    )


def validate_request(
    request: dict[str, Any],
    user_permissions: dict[str, Any] | None = None,
    config: GuardianConfig | None = None,
) -> ValidationResult:
    """Compatibility entry point for legacy, pre-bound workshop requests.

    Production integrations should use ``guardian.control_plane.validate_proposal``
    so that security attributes are rebound from trusted catalogs rather than
    accepted from this request dictionary.
    """
    return _validate_request_core(request, user_permissions, config)
