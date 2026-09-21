from sentinel_experiments.contracts import Fault, FaultLayer, TrialSpec


def test_spec_digest_is_stable_for_equivalent_specs():
    first = TrialSpec(
        "trial-1",
        "incident-1",
        "adservice",
        faults=(Fault("wrong_service", FaultLayer.PREDICTOR),),
    )
    second = TrialSpec(
        "trial-1",
        "incident-1",
        "adservice",
        faults=(Fault("wrong_service", FaultLayer.PREDICTOR),),
    )
    assert first.spec_digest == second.spec_digest

