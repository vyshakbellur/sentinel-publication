import os
from pathlib import Path

import pytest

from sentinel_experiments import Fault, FaultLayer, TrialSpec, run_trial
from sentinel_experiments.policy_baselines import AlwaysDenySubject

OPA_BINARY = os.environ.get("SENTINEL_OPA_BIN")


def proposal(service: str = "adservice"):
    return {
        "capability_name": "set_replicas",
        "arguments": {"service": service, "replicas": 2},
    }


def test_always_deny_never_grants_authority():
    decision = AlwaysDenySubject().decide(proposal())
    assert not decision.allowed
    assert decision.reason_codes == ("ALWAYS_DENY_BASELINE",)


@pytest.mark.skipif(not OPA_BINARY, reason="set SENTINEL_OPA_BIN for OPA integration")
def test_opa_matches_guardian_effect_outcomes_on_frozen_pairs():
    assert Path(OPA_BINARY).is_file()
    for faults in ((), (Fault("wrong_service", FaultLayer.PREDICTOR),)):
        guardian = run_trial(
            TrialSpec("guardian", "incident", "adservice", faults=faults)
        )
        opa = run_trial(
            TrialSpec(
                "opa",
                "incident",
                "adservice",
                guardrail="external_policy",
                faults=faults,
            )
        )
        assert opa.decision.allowed == guardian.decision.allowed
        assert opa.oracle == guardian.oracle


@pytest.mark.skipif(not OPA_BINARY, reason="set SENTINEL_OPA_BIN for OPA integration")
def test_opa_policy_fault_expands_scope_like_guardian_policy_fault():
    faults = (
        Fault("wrong_service", FaultLayer.PREDICTOR),
        Fault("overbroad_scope", FaultLayer.POLICY),
    )
    record = run_trial(
        TrialSpec(
            "opa-overbroad",
            "incident",
            "adservice",
            guardrail="external_policy",
            faults=faults,
        )
    )
    assert record.decision.allowed
    assert record.oracle.unauthorized_effect
