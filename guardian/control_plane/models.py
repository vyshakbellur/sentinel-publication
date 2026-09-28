"""Data contracts for trusted attribute binding.

The model deliberately separates the small, attacker-controlled proposal from
the canonical action evaluated by Guardian.  A proposal cannot carry security
labels.  Those labels are populated by the binder from trusted catalogs and
adapter evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Mapping


class BindingError(ValueError):
    """A fail-closed trusted-binding failure with a stable reason code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _copy_json(value: Any, path: str = "$") -> Any:
    """Validate, normalize, and detach a JSON-compatible value."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise BindingError("ARGUMENT_NOT_FINITE", f"{path} must be finite")
        return value
    if isinstance(value, list):
        return [_copy_json(item, f"{path}[]") for item in value]
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise BindingError("NON_STRING_KEY", f"{path} contains a non-string key")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise BindingError(
                    "NORMALIZED_KEY_COLLISION",
                    f"{path} contains keys that collide after Unicode normalization",
                )
            normalized[normalized_key] = _copy_json(item, f"{path}.{key}")
        return normalized
    raise BindingError(
        "NON_JSON_ARGUMENT",
        f"{path} contains unsupported type {type(value).__name__}",
    )


def canonical_json(value: Any) -> bytes:
    """Return stable UTF-8 JSON for hashing within this reference runtime."""
    normalized = _copy_json(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class AgentProposal:
    """The complete set of fields an untrusted agent may propose."""

    capability_name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> AgentProposal:
        if not isinstance(value, Mapping):
            raise BindingError("PROPOSAL_NOT_OBJECT", "agent proposal must be an object")
        allowed = {"capability_name", "arguments"}
        extras = set(value) - allowed
        if extras:
            raise BindingError(
                "AGENT_ASSERTED_AUTHORITY",
                f"agent proposal contains forbidden fields: {sorted(extras)}",
            )
        name = value.get("capability_name")
        arguments = value.get("arguments", {})
        if not isinstance(name, str) or not name.strip():
            raise BindingError("CAPABILITY_INVALID", "capability_name must be non-empty")
        if not isinstance(arguments, Mapping):
            raise BindingError("ARGUMENTS_NOT_OBJECT", "arguments must be an object")
        return cls(name.strip(), _copy_json(arguments, "$.arguments"))


@dataclass(frozen=True)
class ArgumentSpec:
    """Protocol-neutral JSON argument rule from a trusted manifest."""

    json_type: str
    required: bool = False


@dataclass(frozen=True)
class CapabilityDefinition:
    """Authoritative capability facts supplied by the tool manifest."""

    name: str
    intent: str
    operation: str
    arguments: Mapping[str, ArgumentSpec]
    fixed_destination_id: str | None = None
    destination_argument: str | None = None
    resource_argument: str | None = None
    source_classification: str = "public"
    effects: tuple[str, ...] = ()
    allowed_protocols: frozenset[str] = frozenset()
    bind_all_arguments: bool = False

    def manifest_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "intent": self.intent,
            "operation": self.operation,
            "arguments": {
                name: {"json_type": spec.json_type, "required": spec.required}
                for name, spec in sorted(self.arguments.items())
            },
            "fixed_destination_id": self.fixed_destination_id,
            "destination_argument": self.destination_argument,
            "resource_argument": self.resource_argument,
            "source_classification": self.source_classification,
            "effects": list(self.effects),
            "allowed_protocols": sorted(self.allowed_protocols),
            "bind_all_arguments": self.bind_all_arguments,
        }


@dataclass(frozen=True)
class ResourceDefinition:
    """Authoritative resource metadata returned by a resource catalog."""

    resource_id: str
    classification: str
    tenant_id: str
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DestinationDefinition:
    """Authoritative destination metadata returned by a destination catalog."""

    destination_id: str
    trust_domain: str
    endpoint: str
    tenant_id: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BindingContext:
    """Evidence supplied by trusted adapters and identity/session services."""

    principal: Mapping[str, Any]
    agent: Mapping[str, Any]
    delegation: Mapping[str, Any]
    session: Mapping[str, Any]
    protocol_evidence: Mapping[str, Any]
    authenticated_capability: str
    policy_version: str
    tenant_id: str
    resource_id: str | None = None
    destination_id: str | None = None
    input_provenance: tuple[str, ...] = ()
    presented_manifest_digest: str | None = None
    authorized_arguments: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class CanonicalAction:
    """A canonical action whose security attributes were bound by Guardian."""

    principal: Mapping[str, Any]
    agent: Mapping[str, Any]
    delegation: Mapping[str, Any]
    capability: Mapping[str, Any]
    resource: Mapping[str, Any]
    arguments: Mapping[str, Any]
    input_provenance: tuple[str, ...]
    destination: Mapping[str, Any]
    session: Mapping[str, Any]
    manifest_digest: str
    policy_version: str
    protocol_evidence: Mapping[str, Any]

    def to_envelope(self) -> dict[str, Any]:
        return _copy_json(
            {
                "principal": self.principal,
                "agent": self.agent,
                "delegation": self.delegation,
                "capability": self.capability,
                "resource": self.resource,
                "arguments": self.arguments,
                "input_provenance": list(self.input_provenance),
                "destination": self.destination,
                "session": self.session,
                "manifest_digest": self.manifest_digest,
                "policy_version": self.policy_version,
                "protocol_evidence": self.protocol_evidence,
            }
        )

    @property
    def evidence_digest(self) -> str:
        return hashlib.sha256(canonical_json(self.to_envelope())).hexdigest()

    def to_guardian_request(self) -> dict[str, Any]:
        """Adapt the canonical envelope to the current v1 policy pipeline."""
        resource_id = self.resource.get("id")
        classification = self.resource.get(
            "classification", self.capability["source_classification"]
        )
        target = resource_id or self.capability["name"]
        return {
            "tool_name": self.capability["name"],
            "operation": self.capability["operation"],
            "parameters": _copy_json(self.arguments),
            "target": target,
            "source": {"classification": classification},
            "destination": {
                "trust_domain": self.destination["trust_domain"],
                "id": self.destination["id"],
                "endpoint": self.destination["endpoint"],
            },
            "inputs": list(self.input_provenance),
            "outputs": [],
            "_binding": {
                "manifest_digest": self.manifest_digest,
                "policy_version": self.policy_version,
                "evidence_digest": self.evidence_digest,
            },
        }
