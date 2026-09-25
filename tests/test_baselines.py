from sentinel_experiments.baselines import SchemaAllowlistSubject
from sentinel_experiments.harness import run_matrix
from sentinel_experiments.matrix import baseline_matrix
from sentinel_experiments.reporting import summarize


def test_schema_allowlist_accepts_known_well_typed_action():
    decision = SchemaAllowlistSubject().decide(
        {
            "capability_name": "set_replicas",
            "arguments": {"service": "adservice", "replicas": 2},
        }
    )
    assert decision.allowed
    assert decision.canonical_service == "adservice"


def test_schema_allowlist_rejects_unknown_resource():
    decision = SchemaAllowlistSubject().decide(
        {
            "capability_name": "set_replicas",
            "arguments": {"service": "unknown", "replicas": 2},
        }
    )
    assert not decision.allowed
    assert decision.reason_codes == ("RESOURCE_NOT_ALLOWLISTED",)


def test_schema_allowlist_rejects_extra_authority_fields():
    decision = SchemaAllowlistSubject().decide(
        {
            "capability_name": "set_replicas",
            "arguments": {"service": "adservice", "replicas": 2},
            "tenant_id": "tenant-a",
        }
    )
    assert not decision.allowed
    assert decision.reason_codes == ("SCHEMA_TOP_LEVEL_FIELDS",)


def test_baseline_matrix_replays_identical_proposals_across_guardrails():
    records = run_matrix(baseline_matrix())
    grouped = {
        (record.guardrail, record.trial_id.rsplit("-", 2)[-2:][0]): record
        for record in records
    }
    nominal_proposals = {
        record.guardrail: record.proposal
        for record in records
        if record.trial_id.endswith("-nominal")
    }
    wrong_proposals = {
        record.guardrail: record.proposal
        for record in records
        if record.trial_id.endswith("-wrong-prediction")
    }
    assert len(grouped) == 6
    assert len({str(value) for value in nominal_proposals.values()}) == 1
    assert len({str(value) for value in wrong_proposals.values()}) == 1


def test_trusted_binding_contains_error_static_allowlist_does_not():
    records = run_matrix(baseline_matrix())
    wrong = {
        record.guardrail: record
        for record in records
        if record.trial_id.endswith("-wrong-prediction")
    }
    assert wrong["none"].oracle.unauthorized_effect
    assert wrong["schema_allowlist"].oracle.unauthorized_effect
    assert not wrong["guardian"].oracle.unauthorized_effect
    assert not wrong["guardian"].oracle.recovered
    summary = summarize(records)
    assert summary["by_guardrail"]["guardian"]["unauthorized_effects"] == 0
