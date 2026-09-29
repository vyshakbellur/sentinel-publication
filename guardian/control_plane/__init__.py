"""Trusted binding primitives for Guardian's protocol-neutral control plane."""

from guardian.control_plane.binder import TrustedAttributeBinder
from guardian.control_plane.catalogs import (
    CapabilityCatalog,
    DestinationCatalog,
    ResourceCatalog,
)
from guardian.control_plane.models import (
    AgentProposal,
    ArgumentSpec,
    BindingContext,
    BindingError,
    CanonicalAction,
    CapabilityDefinition,
    DestinationDefinition,
    ResourceDefinition,
)
from guardian.control_plane.pipeline import BoundValidationResult, validate_proposal
from guardian.control_plane.execution import (
    ExecutionVerification,
    envelope_digest,
    verify_execution_envelope,
)

__all__ = [
    "AgentProposal",
    "ArgumentSpec",
    "BindingContext",
    "BindingError",
    "BoundValidationResult",
    "CanonicalAction",
    "CapabilityCatalog",
    "CapabilityDefinition",
    "DestinationCatalog",
    "DestinationDefinition",
    "ExecutionVerification",
    "ResourceCatalog",
    "ResourceDefinition",
    "TrustedAttributeBinder",
    "envelope_digest",
    "validate_proposal",
    "verify_execution_envelope",
]
