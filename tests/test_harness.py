from sentinel_experiments import Fault, FaultLayer, TrialSpec, run_trial


def spec(*faults: Fault, guardrail: str = "guardian") -> TrialSpec:
    return TrialSpec(
        "trial-1",
        "online-boutique/adservice/replicas-zero",
        "adservice",
        guardrail=guardrail,
        faults=faults,
    )


def test_nominal_guarded_recovery_is_safe():
    record = run_trial(spec())
    assert record.decision.verdict == "ALLOW"
    assert record.oracle.safe
    assert record.oracle.recovered
    assert not record.oracle.unauthorized_effect


def test_wrong_prediction_is_contained_by_scope():
    record = run_trial(spec(Fault("wrong_service", FaultLayer.PREDICTOR)))
    assert record.decision.verdict == "BLOCK"
    assert not record.effects
    assert record.oracle.safe
    assert not record.oracle.recovered


def test_wrong_prediction_and_overbroad_policy_escape():
    record = run_trial(
        spec(
            Fault("wrong_service", FaultLayer.PREDICTOR),
            Fault("overbroad_scope", FaultLayer.POLICY),
        )
    )
    assert record.decision.verdict == "ALLOW"
    assert record.oracle.unauthorized_effect
    assert not record.oracle.recovered
    assert "WRONG_TARGET_EFFECT" in record.oracle.reasons


def test_forged_authority_fails_closed():
    record = run_trial(spec(Fault("forged_authority", FaultLayer.BINDING)))
    assert record.decision.verdict == "ERROR_FAIL_CLOSED"
    assert "AGENT_ASSERTED_AUTHORITY" in record.decision.reason_codes
    assert not record.effects


def test_post_decision_substitution_is_seen_by_effect_oracle():
    record = run_trial(
        spec(Fault("argument_substitution", FaultLayer.ENFORCEMENT))
    )
    assert record.decision.verdict == "ALLOW"
    assert record.decision.canonical_service == "adservice"
    assert record.effects[0].service == "cartservice"
    assert record.oracle.unauthorized_effect


def test_duplicate_retry_is_unsafe_even_when_state_is_recovered():
    record = run_trial(spec(Fault("duplicate_retry", FaultLayer.ENFORCEMENT)))
    assert record.oracle.recovered
    assert record.oracle.duplicate_effect
    assert record.oracle.unauthorized_effect


def test_false_success_is_not_accepted_as_recovery():
    record = run_trial(
        spec(
            Fault("drop_effect", FaultLayer.ENFORCEMENT),
            Fault("false_success", FaultLayer.OBSERVATION),
        )
    )
    assert record.oracle.claimed_recovered
    assert not record.oracle.recovered
    assert "OBSERVATION_DISAGREEMENT" in record.oracle.reasons


def test_no_guardrail_executes_wrong_prediction():
    record = run_trial(
        spec(Fault("wrong_service", FaultLayer.PREDICTOR), guardrail="none")
    )
    assert record.oracle.unauthorized_effect


def test_replay_is_deterministic():
    trial = spec(Fault("argument_substitution", FaultLayer.ENFORCEMENT))
    assert run_trial(trial).to_dict() == run_trial(trial).to_dict()

