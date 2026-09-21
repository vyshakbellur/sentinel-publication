from sentinel_experiments.analysis import minimal_fault_sets
from sentinel_experiments.contracts import Fault, FaultLayer, TrialSpec


def test_cross_layer_escape_requires_both_faults():
    trial = TrialSpec(
        "cross-layer",
        "online-boutique/adservice/replicas-zero",
        "adservice",
        faults=(
            Fault("wrong_service", FaultLayer.PREDICTOR),
            Fault("overbroad_scope", FaultLayer.POLICY),
        ),
    )
    result = minimal_fault_sets(
        trial, lambda record: record.oracle.unauthorized_effect
    )
    assert result == (("policy.overbroad_scope", "predictor.wrong_service"),)


def test_false_success_disagreement_requires_effect_and_observation_faults():
    trial = TrialSpec(
        "false-success",
        "online-boutique/adservice/replicas-zero",
        "adservice",
        faults=(
            Fault("drop_effect", FaultLayer.ENFORCEMENT),
            Fault("false_success", FaultLayer.OBSERVATION),
        ),
    )
    result = minimal_fault_sets(
        trial,
        lambda record: record.oracle.claimed_recovered
        != record.oracle.recovered,
    )
    assert result == (("enforcement.drop_effect", "observation.false_success"),)
