"""Trusted Attribute Binder implementation."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from guardian.control_plane.catalogs import (
    CapabilityCatalog,
    DestinationCatalog,
    ResourceCatalog,
)
from guardian.control_plane.models import (
    AgentProposal,
    BindingContext,
    BindingError,
    CanonicalAction,
    CapabilityDefinition,
    DestinationDefinition,
    _copy_json,
    canonical_json,
)
from guardian.layers.classifier import IntentType


_JSON_TYPES: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "integer": (int,),
    "number": (int, float),
    "boolean": (bool,),
    "object": (dict,),
    "array": (list,),
}

_INTENT_OPERATIONS: dict[IntentType, frozenset[str]] = {
    IntentType.READ: frozenset({"read"}),
    IntentType.WRITE: frozenset({"modify"}),
    IntentType.TRANSFORM: frozenset({"encode"}),
    IntentType.TRANSMIT: frozenset({"transmit"}),
    IntentType.TRADE: frozenset({"transmit"}),
    IntentType.ADMIN: frozenset({"execute", "modify"}),
    IntentType.EXFILTRATION: frozenset({"transmit"}),
    IntentType.EXECUTION: frozenset({"execute"}),
    IntentType.UNKNOWN: frozenset(),
}


class TrustedAttributeBinder:
    """Convert an untrusted proposal into a catalog-bound canonical action."""

    def __init__(
        self,
        capabilities: CapabilityCatalog,
        resources: ResourceCatalog,
        destinations: DestinationCatalog,
    ):
        self.capabilities = capabilities
        self.resources = resources
        self.destinations = destinations

    def bind(
        self, proposal: AgentProposal, context: BindingContext
    ) -> CanonicalAction:
        self._validate_context(context)
        capability = self.capabilities.resolve(proposal.capability_name)
        self._validate_capability(capability, context)
        arguments = self._validate_arguments(capability, proposal.arguments)
        authorized_arguments = self._bind_authorized_arguments(
            capability, arguments, context
        )

        resource_id = context.resource_id
        if resource_id is None and capability.resource_argument:
            value = arguments.get(capability.resource_argument)
            resource_id = value if isinstance(value, str) else None

        resource: dict[str, Any] = {}
        if resource_id is not None:
            resolved = self.resources.resolve(resource_id, context.tenant_id)
            resource = {
                "id": resolved.resource_id,
                "classification": resolved.classification,
                "tenant_id": resolved.tenant_id,
                "attributes": _copy_json(resolved.attributes),
            }

        destination = self._resolve_destination(capability, arguments, context)
        if capability.destination_argument:
            # The broker must execute the same normalized URL that policy saw.
            arguments[capability.destination_argument] = destination.endpoint
        manifest_digest = self.capabilities.manifest_digest
        if (
            context.presented_manifest_digest is not None
            and context.presented_manifest_digest != manifest_digest
        ):
            raise BindingError(
                "MANIFEST_DIGEST_MISMATCH",
                "adapter manifest digest does not match the trusted catalog",
            )

        protocol_evidence = _copy_json(context.protocol_evidence)
        protocol_evidence.update(
            {
                "authenticated_capability": context.authenticated_capability,
                "tenant_id": context.tenant_id,
            }
        )
        if authorized_arguments is not None:
            protocol_evidence["authorized_arguments_digest"] = hashlib.sha256(
                canonical_json(authorized_arguments)
            ).hexdigest()

        return CanonicalAction(
            principal=_copy_json(context.principal),
            agent=_copy_json(context.agent),
            delegation=_copy_json(context.delegation),
            capability={
                "name": capability.name,
                "intent": capability.intent,
                "operation": capability.operation,
                "source_classification": capability.source_classification,
                "effects": list(capability.effects),
            },
            resource=resource,
            arguments=arguments,
            input_provenance=tuple(context.input_provenance),
            destination={
                "id": destination.destination_id,
                "trust_domain": destination.trust_domain,
                "endpoint": destination.endpoint,
                "tenant_id": destination.tenant_id,
                "attributes": _copy_json(destination.attributes),
            },
            session=_copy_json(context.session),
            manifest_digest=manifest_digest,
            policy_version=context.policy_version,
            protocol_evidence=protocol_evidence,
        )

    @staticmethod
    def _validate_context(context: BindingContext) -> None:
        required_mappings = {
            "principal": context.principal,
            "agent": context.agent,
            "session": context.session,
            "protocol_evidence": context.protocol_evidence,
        }
        for name, value in required_mappings.items():
            if not isinstance(value, dict) or (
                name != "protocol_evidence" and not value.get("id")
            ):
                raise BindingError(
                    "TRUSTED_CONTEXT_INVALID", f"trusted {name} evidence is incomplete"
                )
        required_strings = {
            "authenticated_capability": context.authenticated_capability,
            "policy_version": context.policy_version,
            "tenant_id": context.tenant_id,
        }
        for name, value in required_strings.items():
            if not isinstance(value, str) or not value.strip():
                raise BindingError(
                    "TRUSTED_CONTEXT_INVALID", f"trusted {name} is missing"
                )
        if context.principal.get("tenant_id") != context.tenant_id:
            raise BindingError(
                "PRINCIPAL_TENANT_MISMATCH",
                "authenticated principal is not bound to the requested tenant",
            )
        if context.session.get("tenant_id") != context.tenant_id:
            raise BindingError(
                "SESSION_TENANT_MISMATCH",
                "session is not bound to the authenticated tenant",
            )
        protocol = context.protocol_evidence.get("protocol")
        if not isinstance(protocol, str) or not protocol:
            raise BindingError(
                "PROTOCOL_EVIDENCE_INVALID", "trusted protocol identity is missing"
            )
        if not all(isinstance(item, str) and item for item in context.input_provenance):
            raise BindingError(
                "PROVENANCE_INVALID", "input provenance must contain non-empty receipt IDs"
            )

    @staticmethod
    def _validate_capability(
        capability: CapabilityDefinition, context: BindingContext
    ) -> None:
        if capability.name != context.authenticated_capability:
            raise BindingError(
                "CAPABILITY_EVIDENCE_MISMATCH",
                "proposed capability does not match authenticated protocol evidence",
            )
        try:
            intent = IntentType(capability.intent)
        except ValueError as exc:
            raise BindingError(
                "MANIFEST_INTENT_INVALID", "manifest intent is not recognized"
            ) from exc
        if capability.operation not in _INTENT_OPERATIONS[intent]:
            raise BindingError(
                "MANIFEST_INTENT_OPERATION_MISMATCH",
                f"intent {intent.value} cannot authorize operation {capability.operation!r}",
            )
        protocol = context.protocol_evidence.get("protocol")
        if capability.allowed_protocols and protocol not in capability.allowed_protocols:
            raise BindingError(
                "PROTOCOL_NOT_ALLOWED",
                f"capability is not registered for protocol {protocol!r}",
            )

    @staticmethod
    def _validate_arguments(
        capability: CapabilityDefinition, proposed: Any
    ) -> dict[str, Any]:
        if not isinstance(proposed, dict):
            proposed = dict(proposed)
        unknown = set(proposed) - set(capability.arguments)
        if unknown:
            raise BindingError(
                "UNKNOWN_ARGUMENT", f"arguments are not in the manifest: {sorted(unknown)}"
            )
        normalized = _copy_json(proposed, "$.arguments")
        for name, spec in capability.arguments.items():
            if spec.required and name not in normalized:
                raise BindingError(
                    "REQUIRED_ARGUMENT_MISSING", f"required argument {name!r} is missing"
                )
            if name not in normalized:
                continue
            expected = _JSON_TYPES.get(spec.json_type)
            if expected is None:
                raise BindingError(
                    "MANIFEST_SCHEMA_INVALID",
                    f"unsupported JSON type {spec.json_type!r} for {name!r}",
                )
            value = normalized[name]
            if spec.json_type in {"integer", "number"} and isinstance(value, bool):
                valid = False
            else:
                valid = isinstance(value, expected)
            if not valid:
                raise BindingError(
                    "ARGUMENT_TYPE_MISMATCH",
                    f"argument {name!r} must be {spec.json_type}",
                )
        return normalized

    def _bind_authorized_arguments(
        self,
        capability: CapabilityDefinition,
        proposed: dict[str, Any],
        context: BindingContext,
    ) -> dict[str, Any] | None:
        """Fail closed when a tuple-bound capability differs from trusted intent."""
        if not capability.bind_all_arguments:
            return None
        if context.authorized_arguments is None:
            raise BindingError(
                "AUTHORIZED_ARGUMENTS_MISSING",
                "capability requires a complete trusted argument tuple",
            )
        if not isinstance(context.authorized_arguments, Mapping):
            raise BindingError(
                "TRUSTED_CONTEXT_INVALID",
                "authorized arguments must be a trusted mapping",
            )
        authorized = self._validate_arguments(
            capability, context.authorized_arguments
        )
        if set(proposed) != set(authorized):
            raise BindingError(
                "AUTHORIZED_ARGUMENT_SET_MISMATCH",
                "proposed argument names differ from the trusted tuple",
            )
        if canonical_json(proposed) != canonical_json(authorized):
            raise BindingError(
                "AUTHORIZED_ARGUMENT_VALUE_MISMATCH",
                "proposed argument values differ from the trusted tuple",
            )
        return authorized

    def _resolve_destination(
        self,
        capability: CapabilityDefinition,
        arguments: dict[str, Any],
        context: BindingContext,
    ) -> DestinationDefinition:
        destination_id = context.destination_id or capability.fixed_destination_id
        if destination_id is not None:
            return self.destinations.resolve_id(destination_id, context.tenant_id)
        if capability.destination_argument:
            locator = arguments.get(capability.destination_argument)
            if not isinstance(locator, str):
                raise BindingError(
                    "DESTINATION_ARGUMENT_INVALID",
                    "destination argument must be a URL string",
                )
            return self.destinations.resolve_url(locator, context.tenant_id)
        raise BindingError(
            "DESTINATION_UNRESOLVED",
            "capability has no trusted destination binding rule",
        )
