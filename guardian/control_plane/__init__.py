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
    "ResourceCatalog",
    "ResourceDefinition",
    "TrustedAttributeBinder",
    "validate_proposal",
]
