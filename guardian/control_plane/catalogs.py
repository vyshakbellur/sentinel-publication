"""In-memory trusted catalogs used by the reference binder."""

from __future__ import annotations

import hashlib
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

from guardian.control_plane.models import (
    BindingError,
    CapabilityDefinition,
    DestinationDefinition,
    ResourceDefinition,
    canonical_json,
)


class CapabilityCatalog:
    def __init__(self, capabilities: Iterable[CapabilityDefinition]):
        items = list(capabilities)
        self._items = {item.name: item for item in items}
        if len(self._items) != len(items):
            raise ValueError("duplicate capability name")

    def resolve(self, name: str) -> CapabilityDefinition:
        try:
            return self._items[name]
        except KeyError as exc:
            raise BindingError(
                "UNKNOWN_CAPABILITY", f"capability {name!r} is not registered"
            ) from exc

    @property
    def manifest_digest(self) -> str:
        records = [self._items[name].manifest_record() for name in sorted(self._items)]
        return hashlib.sha256(canonical_json(records)).hexdigest()


class ResourceCatalog:
    def __init__(self, resources: Iterable[ResourceDefinition]):
        items = list(resources)
        self._items = {item.resource_id: item for item in items}
        if len(self._items) != len(items):
            raise ValueError("duplicate resource id")

    def resolve(self, resource_id: str, tenant_id: str) -> ResourceDefinition:
        try:
            resource = self._items[resource_id]
        except KeyError as exc:
            raise BindingError(
                "UNKNOWN_RESOURCE", f"resource {resource_id!r} is not registered"
            ) from exc
        if resource.tenant_id != tenant_id:
            raise BindingError(
                "RESOURCE_TENANT_MISMATCH",
                f"resource {resource_id!r} does not belong to the authenticated tenant",
            )
        return resource


def normalize_http_url(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BindingError("DESTINATION_INVALID", "destination URL must be non-empty")
    parsed = urlsplit(value.strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        raise BindingError("DESTINATION_SCHEME_DENIED", "only HTTP(S) is supported")
    if parsed.username or parsed.password or not parsed.hostname:
        raise BindingError("DESTINATION_INVALID", "destination URL is malformed")
    try:
        host = parsed.hostname.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise BindingError("DESTINATION_INVALID", "destination host is invalid") from exc
    port = parsed.port
    if port is not None and not (
        (parsed.scheme.lower() == "http" and port == 80)
        or (parsed.scheme.lower() == "https" and port == 443)
    ):
        host = f"{host}:{port}"
    return urlunsplit(
        (parsed.scheme.lower(), host, parsed.path or "/", parsed.query, "")
    )


class DestinationCatalog:
    def __init__(self, destinations: Iterable[DestinationDefinition]):
        items = list(destinations)
        self._items = {item.destination_id: item for item in items}
        if len(self._items) != len(items):
            raise ValueError("duplicate destination id")
        self._hosts: dict[str, DestinationDefinition] = {}
        for item in items:
            normalized = normalize_http_url(item.endpoint)
            hostname = urlsplit(normalized).hostname
            if hostname:
                if hostname in self._hosts:
                    raise ValueError(f"duplicate destination host {hostname!r}")
                self._hosts[hostname] = item

    def resolve_id(self, destination_id: str, tenant_id: str) -> DestinationDefinition:
        try:
            destination = self._items[destination_id]
        except KeyError as exc:
            raise BindingError(
                "UNKNOWN_DESTINATION",
                f"destination {destination_id!r} is not registered",
            ) from exc
        if destination.tenant_id not in (None, tenant_id):
            raise BindingError(
                "DESTINATION_TENANT_MISMATCH",
                "destination does not belong to the authenticated tenant",
            )
        return destination

    def resolve_url(self, value: str, tenant_id: str) -> DestinationDefinition:
        normalized = normalize_http_url(value)
        host = urlsplit(normalized).hostname
        registered = self._hosts.get(host or "")
        if registered is not None:
            if registered.tenant_id not in (None, tenant_id):
                raise BindingError(
                    "DESTINATION_TENANT_MISMATCH",
                    "destination does not belong to the authenticated tenant",
                )
            return DestinationDefinition(
                registered.destination_id,
                registered.trust_domain,
                normalized,
                registered.tenant_id,
                registered.attributes,
            )
        return DestinationDefinition(
            destination_id=f"unregistered:{host}",
            trust_domain="external_untrusted",
            endpoint=normalized,
            tenant_id=None,
            attributes={"registered": False},
        )
