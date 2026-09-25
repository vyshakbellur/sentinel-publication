"""Uniform decision boundary for every frozen guardrail condition."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .baselines import SchemaAllowlistSubject
from .contracts import Decision
from .guardian_adapter import GuardianSubject
from .policy_baselines import AlwaysDenySubject, OpaPolicySubject


def decide_proposal(
    guardrail: str,
    proposal: Mapping[str, Any],
    *,
    expected_service: str,
    services: tuple[str, ...],
    faults: frozenset[str] = frozenset(),
) -> Decision:
    """Evaluate one proposal without coupling the caller to an implementation."""
    if guardrail == "guardian":
        return GuardianSubject(services).decide(
            proposal,
            expected_service=expected_service,
            faults=faults,
        )
    if guardrail == "schema_allowlist":
        return SchemaAllowlistSubject(services).decide(proposal)
    if guardrail == "external_policy":
        return OpaPolicySubject(services).decide(
            proposal,
            expected_service=expected_service,
            faults=faults,
        )
    if guardrail == "always_deny":
        return AlwaysDenySubject().decide(proposal)
    if guardrail == "none":
        service = proposal.get("arguments", {}).get("service")
        return Decision(
            verdict="ALLOW",
            allowed=True,
            canonical_service=service if isinstance(service, str) else None,
            reason_codes=("NO_EXTERNAL_GUARDRAIL",),
        )
    raise ValueError(f"unsupported guardrail {guardrail!r}")
