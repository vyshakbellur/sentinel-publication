"""
Guardian Config: Security Policies

Defines threat types, risk profiles, and the mapping from RCAEval fault
types to Guardian threat categories.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThreatType(Enum):
    """Guardian threat categories mapped from RCAEval fault types."""
    EXCESSIVE_AGENCY = "EXCESSIVE_AGENCY"   # CPU → agent requests excessive permissions
    EXFILTRATION = "EXFILTRATION"           # MEM → agent accumulates/extracts data
    PROMPT_INJECTION = "PROMPT_INJECTION"   # DELAY → attacker injects via prompts
    SUPPLY_CHAIN = "SUPPLY_CHAIN"          # DISK → compromised dependency
    TOOL_POISONING = "TOOL_POISONING"      # LOSS → corrupted tool responses


# ── RCAEval fault → Guardian threat ──────────────────────────────────────────
FAULT_TO_THREAT: dict[str, ThreatType] = {
    "CPU": ThreatType.EXCESSIVE_AGENCY,
    "MEM": ThreatType.EXFILTRATION,
    "DELAY": ThreatType.PROMPT_INJECTION,
    "DISK": ThreatType.SUPPLY_CHAIN,
    "LOSS": ThreatType.TOOL_POISONING,
}

THREAT_TO_FAULT: dict[ThreatType, str] = {v: k for k, v in FAULT_TO_THREAT.items()}


# ── Threat profiles ─────────────────────────────────────────────────────────
@dataclass(frozen=True)
class ThreatProfile:
    """Characteristics of each threat type for detection tuning."""
    name: str
    description: str
    typical_signals: tuple[str, ...]
    expected_risk_tier: str


THREAT_PROFILES: dict[ThreatType, ThreatProfile] = {
    ThreatType.EXCESSIVE_AGENCY: ThreatProfile(
        name="Excessive Agency",
        description="Agent requests permissions beyond its trust level",
        typical_signals=("cpu_spike", "high_permission_request", "scope_violation"),
        expected_risk_tier="HIGH",
    ),
    ThreatType.EXFILTRATION: ThreatProfile(
        name="Data Exfiltration",
        description="Agent accumulates or extracts sensitive data",
        typical_signals=("memory_spike", "large_payload", "repeated_reads"),
        expected_risk_tier="CRITICAL",
    ),
    ThreatType.PROMPT_INJECTION: ThreatProfile(
        name="Prompt Injection",
        description="Attacker overrides system instructions via input",
        typical_signals=("latency_anomaly", "injection_pattern", "intent_mismatch"),
        expected_risk_tier="CRITICAL",
    ),
    ThreatType.SUPPLY_CHAIN: ThreatProfile(
        name="Supply Chain Attack",
        description="Compromised dependency introduces malicious behavior",
        typical_signals=("disk_io_anomaly", "unexpected_dependency", "modified_tool"),
        expected_risk_tier="HIGH",
    ),
    ThreatType.TOOL_POISONING: ThreatProfile(
        name="Tool Poisoning",
        description="Malicious tool descriptions trick the LLM",
        typical_signals=("packet_loss", "corrupted_response", "data_loss_pattern"),
        expected_risk_tier="CRITICAL",
    ),
}
