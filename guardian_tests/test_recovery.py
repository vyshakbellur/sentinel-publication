"""Tests for Guardian Layer 4: Recovery Engine."""

import pytest

from guardian.layers.recovery import (
    RecoveryConfig,
    RecoveryPlan,
    RecoveryTier,
    execute_safe_actions,
    generate_recovery_plan,
)


class TestRecoveryPlanGeneration:
    """Test recovery plan generation for each threat type."""

    def test_prompt_injection_recovery(self):
        plan = generate_recovery_plan(
            threat_type="prompt_injection",
            risk_tier="HIGH",
            decision="BLOCK",
        )
        assert isinstance(plan, RecoveryPlan)
        assert plan.threat_type == "prompt_injection"
        assert plan.safe_count >= 1
        assert plan.moderate_count >= 1
        # Session revocation should be in SAFE tier
        safe_actions = [a for a in plan.actions if a.tier == RecoveryTier.SAFE]
        assert any("session" in a.action.lower() for a in safe_actions)

    def test_excessive_agency_recovery(self):
        plan = generate_recovery_plan(
            threat_type="excessive_agency",
            risk_tier="CRITICAL",
            decision="BLOCK",
        )
        assert plan.threat_type == "excessive_agency"
        assert plan.dangerous_count >= 1  # Rollback requires human approval
        # Should include permission downgrade
        mod_actions = [a for a in plan.actions if a.tier == RecoveryTier.MODERATE]
        assert any("permission" in a.action.lower() or "scope" in a.action.lower()
                    for a in mod_actions)

    def test_tool_poisoning_recovery(self):
        plan = generate_recovery_plan(
            threat_type="tool_poisoning",
            risk_tier="HIGH",
            decision="BLOCK",
        )
        assert plan.threat_type == "tool_poisoning"
        # Should blocklist the tool
        safe_actions = [a for a in plan.actions if a.tier == RecoveryTier.SAFE]
        assert any("blocklist" in a.action.lower() for a in safe_actions)

    def test_exfiltration_recovery(self):
        plan = generate_recovery_plan(
            threat_type="exfiltration",
            risk_tier="CRITICAL",
            decision="BLOCK",
        )
        assert plan.threat_type == "exfiltration"
        assert plan.critical_count >= 1  # Full audit is CRITICAL tier
        # Should block egress
        safe_actions = [a for a in plan.actions if a.tier == RecoveryTier.SAFE]
        assert any("egress" in a.action.lower() for a in safe_actions)

    def test_supply_chain_recovery(self):
        plan = generate_recovery_plan(
            threat_type="supply_chain",
            risk_tier="HIGH",
            decision="BLOCK",
        )
        assert plan.threat_type == "supply_chain"
        assert len(plan.actions) >= 2

    def test_unknown_threat_escalates(self):
        plan = generate_recovery_plan(
            threat_type="unknown_attack_type",
            risk_tier="CRITICAL",
            decision="BLOCK",
        )
        assert plan.critical_count >= 1
        assert "unknown" in plan.actions[0].action.lower()


class TestRecoveryExecution:
    """Test safe action execution."""

    def test_execute_safe_actions_prompt_injection(self):
        plan = generate_recovery_plan(
            threat_type="prompt_injection",
            risk_tier="HIGH",
            decision="BLOCK",
        )
        executed = execute_safe_actions(plan)
        assert len(executed) >= 1
        assert all(e["status"] == "EXECUTED" for e in executed)
        assert all("executed_at" in e for e in executed)

    def test_execute_safe_actions_only_safe_tier(self):
        """Verify only SAFE-tier auto-execute actions are executed."""
        plan = generate_recovery_plan(
            threat_type="excessive_agency",
            risk_tier="CRITICAL",
            decision="BLOCK",
        )
        executed = execute_safe_actions(plan)
        # Should NOT execute DANGEROUS or MODERATE non-auto actions
        for action in plan.actions:
            if action.tier != RecoveryTier.SAFE or not action.auto_execute:
                assert action.action not in [e["action"] for e in executed]

    def test_no_safe_actions_returns_empty(self):
        """Unknown threats have no SAFE actions."""
        plan = generate_recovery_plan(
            threat_type="unknown_attack_type",
            risk_tier="CRITICAL",
            decision="BLOCK",
        )
        executed = execute_safe_actions(plan)
        assert len(executed) == 0


class TestRecoveryConfig:
    """Test recovery configuration."""

    def test_default_config_values(self):
        config = RecoveryConfig()
        assert config.auto_revoke_session is True
        assert config.quarantine_threshold == 3
        assert config.quarantine_window_seconds == 300
        assert config.forensic_retention_days == 90

    def test_custom_config(self):
        config = RecoveryConfig(
            auto_revoke_session=False,
            quarantine_threshold=5,
        )
        assert config.auto_revoke_session is False
        assert config.quarantine_threshold == 5

    def test_config_is_frozen(self):
        config = RecoveryConfig()
        with pytest.raises(Exception):
            config.auto_revoke_session = False  # type: ignore

    def test_custom_config_affects_plan(self):
        """When auto_revoke_session is False, session revocation is not auto-executed."""
        config = RecoveryConfig(auto_revoke_session=False)
        plan = generate_recovery_plan(
            threat_type="prompt_injection",
            risk_tier="HIGH",
            decision="BLOCK",
            config=config,
        )
        # Session action should exist but not be auto-execute
        session_actions = [
            a for a in plan.actions
            if "session" in a.action.lower() and a.tier == RecoveryTier.SAFE
        ]
        assert len(session_actions) >= 1
        assert session_actions[0].auto_execute is False


class TestRecoveryPlanMetadata:
    """Test recovery plan metadata and counts."""

    def test_plan_counts(self):
        plan = generate_recovery_plan(
            threat_type="exfiltration",
            risk_tier="CRITICAL",
            decision="BLOCK",
        )
        total = plan.safe_count + plan.moderate_count + plan.dangerous_count + plan.critical_count
        assert total == len(plan.actions)

    def test_plan_has_timestamp(self):
        plan = generate_recovery_plan(
            threat_type="prompt_injection",
            risk_tier="HIGH",
            decision="BLOCK",
        )
        assert plan.timestamp > 0

    def test_all_actions_have_rollback(self):
        """Every recovery action must have a rollback strategy."""
        for threat_type in ["prompt_injection", "excessive_agency", "tool_poisoning",
                            "exfiltration", "supply_chain"]:
            plan = generate_recovery_plan(
                threat_type=threat_type,
                risk_tier="HIGH",
                decision="BLOCK",
            )
            for action in plan.actions:
                assert action.rollback, f"Action '{action.action}' missing rollback"
                assert len(action.rollback) > 0
