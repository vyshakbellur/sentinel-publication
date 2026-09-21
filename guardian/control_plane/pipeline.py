"""Secure entry point from an untrusted proposal to Guardian validation."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Mapping

from guardian.control_plane.binder import TrustedAttributeBinder
from guardian.control_plane.models import (
    AgentProposal,
    BindingContext,
    BindingError,
    CanonicalAction,
)
from guardian.layers.classifier import INTENT_RISK_MAP, IntentClassification, IntentType
from guardian.layers.progressive_cost import (
    GuardianConfig,
    ValidationResult,
    _validate_request_core,
)


@dataclass(frozen=True)
class BoundValidationResult:
    canonical_action: CanonicalAction | None
    validation: ValidationResult | None
    reason_codes: tuple[str, ...] = ()

    @property
    def decision(self) -> str:
        if self.validation is None:
            return "ERROR_FAIL_CLOSED"
        return self.validation.decision

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"


def validate_proposal(
    proposal: AgentProposal | Mapping[str, Any],
    context: BindingContext,
    binder: TrustedAttributeBinder,
    user_permissions: dict[str, Any],
    config: GuardianConfig | None = None,
) -> BoundValidationResult:
    """Bind trusted facts, then authorize the resulting canonical action."""
    try:
        parsed = (
            proposal
            if isinstance(proposal, AgentProposal)
            else AgentProposal.from_mapping(proposal)
        )
        action = binder.bind(parsed, context)
    except BindingError as exc:
        return BoundValidationResult(None, None, (exc.code,))
    intent = IntentType(action.capability["intent"])
    trusted_classification = IntentClassification(
        intent=intent,
        risk_tier=INTENT_RISK_MAP[intent],
        confidence=1.0,
        method="trusted_manifest",
        reasoning="intent and operation bound from trusted capability manifest",
        latency_ms=0.0,
        metadata={
            "layer": "classifier",
            "manifest_digest": action.manifest_digest,
            "timestamp": time.time(),
        },
    )
    validation = _validate_request_core(
        action.to_guardian_request(),
        user_permissions,
        config,
        classification_override=trusted_classification,
    )
    return BoundValidationResult(action, validation)
