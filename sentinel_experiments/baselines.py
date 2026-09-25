"""Non-Guardian guardrail baselines used for differential evaluation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import Decision


@dataclass(frozen=True)
class SchemaAllowlistSubject:
    """Validate proposal shape and a static capability/resource allowlist.

    This deliberately has no incident-specific trusted binding. It represents
    the common control that validates a typed tool call and exposes only known
    resources, while trusting the predictor's choice among those resources.
    """

    services: tuple[str, ...] = ("adservice", "cartservice")

    def decide(self, proposal: Mapping[str, Any]) -> Decision:
        if set(proposal) != {"capability_name", "arguments"}:
            return self._block("SCHEMA_TOP_LEVEL_FIELDS")
        if proposal.get("capability_name") != "set_replicas":
            return self._block("CAPABILITY_NOT_ALLOWLISTED")
        arguments = proposal.get("arguments")
        if not isinstance(arguments, Mapping) or set(arguments) != {
            "service",
            "replicas",
        }:
            return self._block("SCHEMA_ARGUMENT_FIELDS")
        service = arguments.get("service")
        replicas = arguments.get("replicas")
        if not isinstance(service, str) or service not in self.services:
            return self._block("RESOURCE_NOT_ALLOWLISTED")
        if isinstance(replicas, bool) or not isinstance(replicas, int) or replicas < 0:
            return self._block("SCHEMA_REPLICAS_TYPE")
        return Decision(
            verdict="ALLOW",
            allowed=True,
            reason_codes=("SCHEMA_ALLOWLIST_PASS",),
            canonical_service=service,
        )

    @staticmethod
    def _block(reason: str) -> Decision:
        return Decision(verdict="BLOCK", allowed=False, reason_codes=(reason,))
