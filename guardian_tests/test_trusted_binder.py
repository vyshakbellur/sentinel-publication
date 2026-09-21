"""Security boundary tests for the Trusted Attribute Binder."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from guardian.control_plane import (
    AgentProposal,
    ArgumentSpec,
    BindingContext,
    BindingError,
    CapabilityCatalog,
    CapabilityDefinition,
    DestinationCatalog,
    DestinationDefinition,
    ResourceCatalog,
    ResourceDefinition,
    TrustedAttributeBinder,
    validate_proposal,
)


@pytest.fixture
def binder() -> TrustedAttributeBinder:
    capabilities = CapabilityCatalog(
        [
            CapabilityDefinition(
                name="get_balance",
                intent="READ",
                operation="read",
                arguments={"account_id": ArgumentSpec("string", required=True)},
                resource_argument="account_id",
                fixed_destination_id="core-banking",
                effects=("read_resource",),
                allowed_protocols=frozenset({"mcp", "rest"}),
            ),
            CapabilityDefinition(
                name="http_post",
                intent="TRANSMIT",
                operation="transmit",
                arguments={
                    "url": ArgumentSpec("string", required=True),
                    "payload_id": ArgumentSpec("string", required=True),
                },
                resource_argument="payload_id",
                destination_argument="url",
                effects=("network_egress", "data_transmission"),
                allowed_protocols=frozenset({"mcp"}),
            ),
        ]
    )
    resources = ResourceCatalog(
        [
            ResourceDefinition("account-1", "confidential", "tenant-a"),
            ResourceDefinition("secret-1", "secret", "tenant-a"),
            ResourceDefinition("other-account", "confidential", "tenant-b"),
        ]
    )
    destinations = DestinationCatalog(
        [
            DestinationDefinition(
                "core-banking",
                "internal_trusted",
                "https://bank.internal.example/api",
                "tenant-a",
            ),
            DestinationDefinition(
                "approved-partner",
                "external_trusted",
                "https://partner.example/upload",
            ),
        ]
    )
    return TrustedAttributeBinder(capabilities, resources, destinations)


def context(
    capability: str,
    *,
    tenant_id: str = "tenant-a",
    resource_id: str | None = None,
    destination_id: str | None = None,
    manifest_digest: str | None = None,
) -> BindingContext:
    return BindingContext(
        principal={"id": "user-1", "tenant_id": tenant_id},
        agent={"id": "agent-1"},
        delegation={"id": "delegation-1"},
        session={"id": "session-1", "tenant_id": tenant_id},
        protocol_evidence={"id": "request-1", "protocol": "mcp"},
        authenticated_capability=capability,
        policy_version="policy-7",
        tenant_id=tenant_id,
        resource_id=resource_id,
        destination_id=destination_id,
        input_provenance=("receipt-1",),
        presented_manifest_digest=manifest_digest,
    )


def permissions(*intents: str, scope: set[str]) -> dict:
    return {
        "allowed_intents": set(intents),
        "allowed_scope": scope,
        "allowed_domains": ["partner.example"],
        "action_history": {},
    }


def test_safe_read_binds_catalog_facts_and_allows(binder):
    proposal = AgentProposal.from_mapping(
        {"capability_name": "get_balance", "arguments": {"account_id": "account-1"}}
    )
    result = validate_proposal(
        proposal,
        context("get_balance"),
        binder,
        permissions("READ", scope={"account-1"}),
    )

    action = result.canonical_action
    assert action.capability["operation"] == "read"
    assert action.capability["intent"] == "READ"
    assert action.resource["classification"] == "confidential"
    assert action.destination["trust_domain"] == "internal_trusted"
    assert result.validation.decision == "ALLOW"
    assert result.validation.classification.method == "trusted_manifest"


def test_bound_action_conforms_to_public_canonical_schema(binder):
    proposal = AgentProposal("get_balance", {"account_id": "account-1"})
    action = binder.bind(proposal, context("get_balance"))
    schema_path = Path(__file__).parent.parent / "guardian/schemas/canonical_action.json"
    jsonschema.validate(action.to_envelope(), json.loads(schema_path.read_text()))


def test_minimal_agent_proposal_conforms_to_public_schema():
    raw = {"capability_name": "get_balance", "arguments": {"account_id": "account-1"}}
    schema_path = Path(__file__).parent.parent / "guardian/schemas/agent_proposal.json"
    jsonschema.validate(raw, json.loads(schema_path.read_text()))


def test_agent_cannot_assert_security_attributes():
    with pytest.raises(BindingError, match="forbidden fields") as exc:
        AgentProposal.from_mapping(
            {
                "capability_name": "get_balance",
                "arguments": {"account_id": "account-1"},
                "operation": "read",
                "source": {"classification": "public"},
            }
        )
    assert exc.value.code == "AGENT_ASSERTED_AUTHORITY"


def test_secure_pipeline_turns_forged_authority_into_fail_closed_decision(binder):
    result = validate_proposal(
        {
            "capability_name": "get_balance",
            "arguments": {"account_id": "account-1"},
            "source": {"classification": "public"},
        },
        context("get_balance"),
        binder,
        permissions("READ", scope={"account-1"}),
    )
    assert result.decision == "ERROR_FAIL_CLOSED"
    assert result.reason_codes == ("AGENT_ASSERTED_AUTHORITY",)
    assert not result.allowed
    assert result.canonical_action is None


def test_unknown_capability_fails_closed(binder):
    proposal = AgentProposal("totally_safe_read", {})
    with pytest.raises(BindingError) as exc:
        binder.bind(proposal, context("totally_safe_read"))
    assert exc.value.code == "UNKNOWN_CAPABILITY"


def test_authenticated_capability_must_match_proposal(binder):
    proposal = AgentProposal("get_balance", {"account_id": "account-1"})
    with pytest.raises(BindingError) as exc:
        binder.bind(proposal, context("http_post"))
    assert exc.value.code == "CAPABILITY_EVIDENCE_MISMATCH"


def test_resource_tenant_cannot_be_crossed(binder):
    proposal = AgentProposal("get_balance", {"account_id": "other-account"})
    with pytest.raises(BindingError) as exc:
        binder.bind(proposal, context("get_balance"))
    assert exc.value.code == "RESOURCE_TENANT_MISMATCH"


def test_secret_to_unregistered_url_is_bound_and_blocked(binder):
    proposal = AgentProposal(
        "http_post",
        {"url": "HTTPS://COLLECTOR.INVALID:443/upload#ignored", "payload_id": "secret-1"},
    )
    result = validate_proposal(
        proposal,
        context("http_post"),
        binder,
        permissions("TRANSMIT", scope={"secret-1"}),
    )

    assert result.canonical_action.arguments["url"] == "https://collector.invalid/upload"
    assert result.canonical_action.destination["trust_domain"] == "external_untrusted"
    assert result.validation.decision == "BLOCK"
    assert any(
        reason == "data_flow_denied:secret_to_external_untrusted"
        for reason in result.validation.verification.checks_failed
    )


def test_agent_cannot_smuggle_unregistered_arguments(binder):
    proposal = AgentProposal(
        "get_balance", {"account_id": "account-1", "trust_domain": "internal_trusted"}
    )
    with pytest.raises(BindingError) as exc:
        binder.bind(proposal, context("get_balance"))
    assert exc.value.code == "UNKNOWN_ARGUMENT"


def test_manifest_digest_mismatch_fails_closed(binder):
    proposal = AgentProposal("get_balance", {"account_id": "account-1"})
    with pytest.raises(BindingError) as exc:
        binder.bind(proposal, context("get_balance", manifest_digest="forged"))
    assert exc.value.code == "MANIFEST_DIGEST_MISMATCH"


def test_same_trusted_inputs_produce_same_evidence_digest(binder):
    proposal = AgentProposal("get_balance", {"account_id": "account-1"})
    first = binder.bind(proposal, context("get_balance"))
    second = binder.bind(proposal, context("get_balance"))
    assert first.evidence_digest == second.evidence_digest


def test_incoherent_manifest_intent_and_operation_is_rejected():
    capabilities = CapabilityCatalog(
        [
            CapabilityDefinition(
                name="disguised_execution",
                intent="READ",
                operation="execute",
                arguments={},
                fixed_destination_id="executor",
            )
        ]
    )
    binder = TrustedAttributeBinder(
        capabilities,
        ResourceCatalog([]),
        DestinationCatalog(
            [
                DestinationDefinition(
                    "executor", "internal_trusted", "https://executor.internal.example"
                )
            ]
        ),
    )
    with pytest.raises(BindingError) as exc:
        binder.bind(AgentProposal("disguised_execution", {}), context("disguised_execution"))
    assert exc.value.code == "MANIFEST_INTENT_OPERATION_MISMATCH"


def test_session_must_be_tenant_bound(binder):
    proposal = AgentProposal("get_balance", {"account_id": "account-1"})
    bad = context("get_balance")
    bad = BindingContext(
        **{**bad.__dict__, "session": {"id": "session-1", "tenant_id": "tenant-b"}}
    )
    with pytest.raises(BindingError) as exc:
        binder.bind(proposal, bad)
    assert exc.value.code == "SESSION_TENANT_MISMATCH"
