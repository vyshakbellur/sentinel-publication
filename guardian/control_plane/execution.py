"""Execution-time verification for policy-authorized canonical actions."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping

from guardian.control_plane.models import canonical_json


@dataclass(frozen=True)
class ExecutionVerification:
    allowed: bool
    reason_code: str
    observed_evidence_digest: str


def envelope_digest(envelope: Mapping[str, Any]) -> str:
    """Hash the exact canonical action presented to the execution broker."""
    return hashlib.sha256(canonical_json(envelope)).hexdigest()


def verify_execution_envelope(
    envelope: Mapping[str, Any], authorized_evidence_digest: str
) -> ExecutionVerification:
    """Reject any action whose execution tuple differs from the policy input."""
    observed = envelope_digest(envelope)
    matched = observed == authorized_evidence_digest
    return ExecutionVerification(
        allowed=matched,
        reason_code=(
            "EVIDENCE_DIGEST_MATCH" if matched else "EVIDENCE_DIGEST_MISMATCH"
        ),
        observed_evidence_digest=observed,
    )
