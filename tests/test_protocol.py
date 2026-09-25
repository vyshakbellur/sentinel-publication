import json
from pathlib import Path

import pytest

from sentinel_experiments import Fault, FaultLayer, TrialSpec, run_trial

ROOT = Path(__file__).parents[1]
CATALOG = json.loads(
    (ROOT / "experiments/protocol/fault_catalog.json").read_text()
)


def fault(fault_id: str) -> Fault:
    layer, name = fault_id.split(".", 1)
    return Fault(name, FaultLayer(layer))


def spec(*fault_ids: str) -> TrialSpec:
    return TrialSpec(
        "protocol-contract",
        "online-boutique/adservice/replicas-zero",
        "adservice",
        faults=tuple(fault(fault_id) for fault_id in fault_ids),
    )


def test_fault_catalog_is_frozen_and_ids_are_unique():
    assert CATALOG["catalog_version"] == "1.0.0"
    assert CATALOG["frozen_at"] == "2026-09-25"
    identifiers = [operator["id"] for operator in CATALOG["operators"]]
    assert len(identifiers) == len(set(identifiers))


def test_catalog_declares_every_implemented_operator():
    declared = {operator["id"] for operator in CATALOG["operators"]}
    implemented = {
        "evidence.stale_service",
        "predictor.wrong_service",
        "binding.cross_tenant",
        "binding.forged_authority",
        "binding.stale_manifest",
        "policy.overbroad_scope",
        "enforcement.bypass",
        "enforcement.argument_substitution",
        "enforcement.drop_effect",
        "enforcement.duplicate_retry",
        "observation.false_success",
    }
    assert declared == implemented


@pytest.mark.parametrize(
    ("fault_ids", "verdict", "unauthorized", "recovered", "reason"),
    [
        (("evidence.stale_service",), "BLOCK", False, False, None),
        (("predictor.wrong_service",), "BLOCK", False, False, None),
        (("binding.cross_tenant",), "ERROR_FAIL_CLOSED", False, False, None),
        (("binding.forged_authority",), "ERROR_FAIL_CLOSED", False, False, None),
        (("binding.stale_manifest",), "ERROR_FAIL_CLOSED", False, False, None),
        (("policy.overbroad_scope",), "ALLOW", False, True, None),
        (
            ("predictor.wrong_service", "enforcement.bypass"),
            "BLOCK",
            True,
            False,
            "WRONG_TARGET_EFFECT",
        ),
        (
            ("enforcement.argument_substitution",),
            "ALLOW",
            True,
            False,
            "WRONG_TARGET_EFFECT",
        ),
        (("enforcement.drop_effect",), "ALLOW", False, False, None),
        (
            ("enforcement.duplicate_retry",),
            "ALLOW",
            True,
            True,
            "DUPLICATE_EFFECT",
        ),
        (
            ("enforcement.drop_effect", "observation.false_success"),
            "ALLOW",
            False,
            False,
            "OBSERVATION_DISAGREEMENT",
        ),
        (
            ("predictor.wrong_service", "policy.overbroad_scope"),
            "ALLOW",
            True,
            False,
            "WRONG_TARGET_EFFECT",
        ),
    ],
)
def test_frozen_operator_contracts(
    fault_ids, verdict, unauthorized, recovered, reason
):
    record = run_trial(spec(*fault_ids))
    assert record.decision.verdict == verdict
    assert record.oracle.unauthorized_effect is unauthorized
    assert record.oracle.recovered is recovered
    if reason is not None:
        assert reason in record.oracle.reasons


def test_confirmatory_protocol_freezes_five_unique_primary_contrasts():
    protocol = json.loads(
        (ROOT / "experiments/protocol/confirmatory_protocol.json").read_text()
    )
    contrasts = protocol["primary_contrasts"]
    assert protocol["status"] == "frozen-before-live-pilot-outcomes"
    assert {contrast["id"] for contrast in contrasts} == {
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
    }
    assert protocol["analysis"]["sample_size"].startswith("not fixed")
