"""Adapter from SENTINEL trials to the local Guardian control plane."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import Decision


class GuardianUnavailable(RuntimeError):
    """Raised when the Guardian package is not importable."""


@dataclass(frozen=True)
class GuardianSubject:
    services: tuple[str, ...] = ("adservice", "cartservice")
    tenant_id: str = "tenant-a"
    trusted_scope_binding: bool = True
    fail_closed: bool = True

    def decide(
        self,
        proposal: Mapping[str, Any],
        *,
        expected_service: str,
        faults: frozenset[str],
    ) -> Decision:
        try:
            from guardian.control_plane import (
                ArgumentSpec,
                BindingContext,
                CapabilityCatalog,
                CapabilityDefinition,
                DestinationCatalog,
                DestinationDefinition,
                ResourceCatalog,
                ResourceDefinition,
                TrustedAttributeBinder,
                validate_proposal,
            )
        except ImportError as exc:
            raise GuardianUnavailable(
                "Guardian is not importable; add its repository to PYTHONPATH"
            ) from exc

        capabilities = CapabilityCatalog(
            [
                CapabilityDefinition(
                    name="set_replicas",
                    intent="WRITE",
                    operation="modify",
                    arguments={
                        "service": ArgumentSpec("string", required=True),
                        "replicas": ArgumentSpec("integer", required=True),
                    },
                    resource_argument="service",
                    fixed_destination_id="kubernetes-api",
                    effects=("scale_workload",),
                    allowed_protocols=frozenset({"mcp"}),
                )
            ]
        )
        resources = ResourceCatalog(
            [
                ResourceDefinition(service, "internal", self.tenant_id)
                for service in self.services
            ]
        )
        destinations = DestinationCatalog(
            [
                DestinationDefinition(
                    "kubernetes-api",
                    "internal_trusted",
                    "https://kubernetes.default.svc",
                    self.tenant_id,
                )
            ]
        )
        binder = TrustedAttributeBinder(capabilities, resources, destinations)

        context_tenant = (
            "tenant-b" if "binding.cross_tenant" in faults else self.tenant_id
        )
        context = BindingContext(
            principal={"id": "operator-1", "tenant_id": context_tenant},
            agent={"id": "aria"},
            delegation={"id": "delegation-1"},
            session={"id": "session-1", "tenant_id": context_tenant},
            protocol_evidence={"id": "request-1", "protocol": "mcp"},
            authenticated_capability="set_replicas",
            policy_version="sentinel-policy-v1",
            tenant_id=context_tenant,
            input_provenance=("telemetry-receipt-1",),
            presented_manifest_digest=(
                "stale-manifest"
                if "binding.stale_manifest" in faults
                else None
            ),
        )

        mutable_proposal = dict(proposal)
        if "binding.forged_authority" in faults:
            mutable_proposal["source"] = {"classification": "public"}

        scope = (
            {expected_service}
            if self.trusted_scope_binding
            and "policy.overbroad_scope" not in faults
            else set(self.services)
        )
        permissions = {
            "allowed_intents": {"WRITE"},
            "allowed_scope": scope,
            "allowed_domains": [],
            "action_history": {},
        }
        result = validate_proposal(mutable_proposal, context, binder, permissions)
        action = result.canonical_action
        service = None if action is None else action.arguments.get("service")
        evidence_digest = None if action is None else action.evidence_digest
        reason_codes = tuple(result.reason_codes)
        if result.validation is not None and result.validation.verification is not None:
            reason_codes += tuple(result.validation.verification.checks_failed)
        decision = Decision(
            verdict=result.decision,
            allowed=result.allowed,
            reason_codes=reason_codes,
            canonical_service=service,
            evidence_digest=evidence_digest,
        )
        if self.fail_closed or decision.verdict != "ERROR_FAIL_CLOSED":
            return decision

        arguments = mutable_proposal.get("arguments", {})
        fallback_service = arguments.get("service")
        return Decision(
            verdict="ALLOW_FAIL_OPEN",
            allowed=True,
            reason_codes=reason_codes + ("ABLATION_PERMISSIVE_FALLBACK",),
            canonical_service=(
                fallback_service if isinstance(fallback_service, str) else None
            ),
            evidence_digest=evidence_digest,
        )
