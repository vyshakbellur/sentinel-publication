"""
Guardian Layer 4: Recovery Engine (Bridged from ARIA's Remediation Layer)

Provides post-incident recovery actions when the Guardian pipeline blocks
or escalates a threat. Actions are risk-tiered to match the Guardian
Paradigm's Progressive Cost principle.

Recovery tiers:
  SAFE      — Automatic, reversible (revoke session, rotate token)
  MODERATE  — Automatic with notification (quarantine agent, reduce scope)
  DANGEROUS — Human approval required (disable agent, revoke permissions)
  CRITICAL  — Full incident response (suspend all agents, forensic audit)

Inspired by ARIA's Layer 4 remediation engine, adapted from microservice
fault recovery to agentic AI threat recovery.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

class RecoveryTier(Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    DANGEROUS = "DANGEROUS"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RecoveryConfig:
    """Configuration for the recovery engine.

    All thresholds are centralized and immutable — same frozen dataclass
    pattern used across ARIA and Guardian.
    """
    # Auto-revoke session on BLOCK decisions
    auto_revoke_session: bool = True
    # Auto-quarantine agent after N blocked requests in a window
    quarantine_threshold: int = 3
    quarantine_window_seconds: int = 300  # 5 minutes
    # Escalation: disable agent entirely after N quarantines
    disable_threshold: int = 2
    # Forensic: retain full audit trail for this many days
    forensic_retention_days: int = 90
    # Recovery: maximum number of auto-recovery attempts
    max_auto_recovery: int = 3


DEFAULT_RECOVERY_CONFIG = RecoveryConfig()


# ─────────────────────────────────────────────────────────────────────────────
# Recovery Action
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RecoveryAction:
    """A single recovery action to execute or recommend."""
    tier: RecoveryTier
    action: str
    rationale: str
    auto_execute: bool
    rollback: str
    target: str  # What entity is affected (agent, session, user, system)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """Complete recovery plan for a detected threat."""
    threat_type: str
    risk_tier: str
    decision: str  # BLOCK, ESCALATE
    actions: list[RecoveryAction]
    timestamp: float = field(default_factory=time.time)
    safe_count: int = 0
    moderate_count: int = 0
    dangerous_count: int = 0
    critical_count: int = 0

    def __post_init__(self):
        self.safe_count = sum(1 for a in self.actions if a.tier == RecoveryTier.SAFE)
        self.moderate_count = sum(1 for a in self.actions if a.tier == RecoveryTier.MODERATE)
        self.dangerous_count = sum(1 for a in self.actions if a.tier == RecoveryTier.DANGEROUS)
        self.critical_count = sum(1 for a in self.actions if a.tier == RecoveryTier.CRITICAL)


# ─────────────────────────────────────────────────────────────────────────────
# Threat-Specific Recovery Strategies
# ─────────────────────────────────────────────────────────────────────────────

def _recover_prompt_injection(
    verification_result: dict,
    config: RecoveryConfig,
) -> list[RecoveryAction]:
    """Recovery for prompt injection attacks."""
    actions = [
        RecoveryAction(
            tier=RecoveryTier.SAFE,
            action="Invalidate current session token",
            rationale=(
                "Prompt injection detected. Session may be compromised — "
                "invalidating forces re-authentication."
            ),
            auto_execute=config.auto_revoke_session,
            rollback="Re-issue session token after manual review",
            target="session",
        ),
        RecoveryAction(
            tier=RecoveryTier.SAFE,
            action="Log full request payload to forensic audit trail",
            rationale="Preserve attack payload for post-incident analysis.",
            auto_execute=True,
            rollback="N/A — logging is non-destructive",
            target="audit_system",
        ),
        RecoveryAction(
            tier=RecoveryTier.MODERATE,
            action="Quarantine agent: restrict to READ-only tools for 5 minutes",
            rationale=(
                "Reduce blast radius by limiting agent capabilities "
                "while the attack vector is investigated."
            ),
            auto_execute=True,
            rollback="Restore full tool access after quarantine window expires",
            target="agent",
        ),
    ]
    return actions


def _recover_excessive_agency(
    verification_result: dict,
    config: RecoveryConfig,
) -> list[RecoveryAction]:
    """Recovery for excessive agency / privilege escalation."""
    actions = [
        RecoveryAction(
            tier=RecoveryTier.SAFE,
            action="Reset agent's action counter and cooldown timer",
            rationale=(
                "Excessive agency detected — agent may have accumulated "
                "permissions through repeated requests. Reset state."
            ),
            auto_execute=True,
            rollback="N/A — state reset is non-destructive",
            target="agent",
        ),
        RecoveryAction(
            tier=RecoveryTier.MODERATE,
            action="Downgrade agent permissions to minimum viable scope",
            rationale=(
                "Agent attempted actions outside its intended scope. "
                "Reduce to READ-only until human reviews."
            ),
            auto_execute=True,
            rollback="Restore permissions after human approval",
            target="agent",
        ),
        RecoveryAction(
            tier=RecoveryTier.DANGEROUS,
            action="Review and rollback any state changes from recent session",
            rationale=(
                "If the agent executed any high-risk actions before detection, "
                "those actions may need compensating transactions."
            ),
            auto_execute=False,
            rollback="Apply compensating transactions as identified",
            target="system",
        ),
    ]
    return actions


def _recover_tool_poisoning(
    verification_result: dict,
    config: RecoveryConfig,
) -> list[RecoveryAction]:
    """Recovery for tool poisoning attacks."""
    actions = [
        RecoveryAction(
            tier=RecoveryTier.SAFE,
            action="Blocklist the suspected tool for this session",
            rationale=(
                "Tool poisoning detected — tool description may contain "
                "malicious instructions. Block until tool is re-verified."
            ),
            auto_execute=True,
            rollback="Remove tool from blocklist after manual verification",
            target="tool_registry",
        ),
        RecoveryAction(
            tier=RecoveryTier.MODERATE,
            action="Validate all tool definitions against trusted manifest",
            rationale=(
                "If one tool is poisoned, others may be compromised. "
                "Compare current tool definitions to the trusted baseline."
            ),
            auto_execute=True,
            rollback="N/A — validation is read-only",
            target="tool_registry",
        ),
        RecoveryAction(
            tier=RecoveryTier.DANGEROUS,
            action="Rebuild tool registry from trusted source",
            rationale=(
                "Multiple poisoned tools indicate a supply chain compromise. "
                "Rebuild the entire tool registry from version control."
            ),
            auto_execute=False,
            rollback="Restore previous tool registry from backup",
            target="tool_registry",
        ),
    ]
    return actions


def _recover_exfiltration(
    verification_result: dict,
    config: RecoveryConfig,
) -> list[RecoveryAction]:
    """Recovery for data exfiltration attempts."""
    actions = [
        RecoveryAction(
            tier=RecoveryTier.SAFE,
            action="Block egress to external destinations for this agent",
            rationale=(
                "Exfiltration detected — agent attempted to send data "
                "to an external endpoint. Block all egress."
            ),
            auto_execute=True,
            rollback="Restore egress permissions after investigation",
            target="network",
        ),
        RecoveryAction(
            tier=RecoveryTier.MODERATE,
            action="Revoke agent's data access tokens",
            rationale=(
                "Agent may have cached sensitive data. Revoking tokens "
                "prevents further data access."
            ),
            auto_execute=True,
            rollback="Re-issue data access tokens after review",
            target="agent",
        ),
        RecoveryAction(
            tier=RecoveryTier.CRITICAL,
            action="Trigger full data access audit for affected resources",
            rationale=(
                "Determine exactly what data was accessed, by whom, "
                "and whether any was successfully exfiltrated."
            ),
            auto_execute=False,
            rollback="N/A — audit is investigative",
            target="audit_system",
        ),
    ]
    return actions


def _recover_supply_chain(
    verification_result: dict,
    config: RecoveryConfig,
) -> list[RecoveryAction]:
    """Recovery for supply chain attacks."""
    actions = [
        RecoveryAction(
            tier=RecoveryTier.SAFE,
            action="Blocklist the suspected package/dependency",
            rationale="Supply chain threat detected — block the dependency.",
            auto_execute=True,
            rollback="Remove from blocklist after package audit",
            target="dependency_registry",
        ),
        RecoveryAction(
            tier=RecoveryTier.DANGEROUS,
            action="Run dependency audit on all agent packages",
            rationale=(
                "A compromised dependency may indicate broader supply "
                "chain issues. Full audit required."
            ),
            auto_execute=False,
            rollback="N/A — audit is read-only",
            target="dependency_registry",
        ),
    ]
    return actions


# ─────────────────────────────────────────────────────────────────────────────
# Recovery Strategy Registry (same pattern as ARIA's signal pipeline)
# ─────────────────────────────────────────────────────────────────────────────

_RECOVERY_STRATEGIES = {
    "prompt_injection": _recover_prompt_injection,
    "excessive_agency": _recover_excessive_agency,
    "tool_poisoning": _recover_tool_poisoning,
    "exfiltration": _recover_exfiltration,
    "supply_chain": _recover_supply_chain,
}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_recovery_plan(
    threat_type: str,
    risk_tier: str,
    decision: str,
    verification_result: dict | None = None,
    config: RecoveryConfig | None = None,
) -> RecoveryPlan:
    """Generate a recovery plan for a detected threat.

    Args:
        threat_type:         One of: prompt_injection, excessive_agency,
                             tool_poisoning, exfiltration, supply_chain.
        risk_tier:           LOW, MEDIUM, HIGH, CRITICAL.
        decision:            BLOCK or ESCALATE.
        verification_result: Full verification result from the Verifier.
        config:              Recovery configuration.

    Returns:
        RecoveryPlan with threat-specific recovery actions.
    """
    cfg = config or DEFAULT_RECOVERY_CONFIG
    vr = verification_result or {}

    strategy = _RECOVERY_STRATEGIES.get(threat_type.lower())
    if strategy is None:
        # Unknown threat type — default to maximum caution
        actions = [
            RecoveryAction(
                tier=RecoveryTier.CRITICAL,
                action="Unknown threat type — trigger full incident response",
                rationale=f"Unrecognized threat: '{threat_type}'. Escalate.",
                auto_execute=False,
                rollback="Resume normal operations after investigation",
                target="system",
            ),
        ]
    else:
        actions = strategy(vr, cfg)

    return RecoveryPlan(
        threat_type=threat_type,
        risk_tier=risk_tier,
        decision=decision,
        actions=actions,
    )


def execute_safe_actions(plan: RecoveryPlan) -> list[dict]:
    """Execute all SAFE-tier auto-execute actions in a recovery plan.

    Returns a list of executed action summaries.
    """
    executed = []
    for action in plan.actions:
        if action.tier == RecoveryTier.SAFE and action.auto_execute:
            executed.append({
                "action": action.action,
                "target": action.target,
                "rationale": action.rationale,
                "rollback": action.rollback,
                "executed_at": time.time(),
                "status": "EXECUTED",
            })
    return executed
