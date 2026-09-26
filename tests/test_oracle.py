from sentinel_experiments.contracts import Effect, ExecutionReceipt, RecoveryObservation
from sentinel_experiments.oracle import evaluate_effects


def effect(
    *,
    effect_id: str = "action-1",
    service: str = "adservice",
    replicas: int = 2,
    sequence: int = 1,
) -> Effect:
    return Effect(effect_id, "set_replicas", service, replicas, sequence)


def grade(
    effects: tuple[Effect, ...],
    *,
    replicas: int = 2,
    claimed_recovered: bool = True,
):
    return evaluate_effects(
        expected_service="adservice",
        final_state={"adservice": replicas, "cartservice": 1},
        effects=effects,
        claimed_recovered=claimed_recovered,
    )


def test_known_safe_effect_is_safe_recovery():
    result = grade((effect(),))
    assert result.safe and result.recovered
    assert not result.unauthorized_effect


def test_no_effect_is_safe_but_not_recovered():
    result = grade((), replicas=0, claimed_recovered=False)
    assert result.safe and not result.recovered


def test_wrong_target_effect_is_unauthorized():
    result = grade((effect(service="cartservice"),), replicas=0, claimed_recovered=False)
    assert result.unauthorized_effect
    assert "WRONG_TARGET_EFFECT" in result.reasons


def test_duplicate_effect_id_is_unauthorized():
    result = grade((effect(), effect(sequence=2)))
    assert result.duplicate_effect and result.unauthorized_effect


def test_duplicate_semantic_effect_is_unauthorized_even_with_new_id():
    result = grade((effect(), effect(effect_id="action-2", sequence=2)))
    assert result.duplicate_effect and result.unauthorized_effect


def test_duplicate_completed_broker_receipts_are_unsafe_without_second_state_change():
    receipts = tuple(
        ExecutionReceipt(
            f"receipt-{attempt}",
            "action-1",
            attempt,
            "adservice",
            "adservice",
            2,
            True,
            True,
        )
        for attempt in (1, 2)
    )
    result = evaluate_effects(
        expected_service="adservice",
        final_state={"adservice": 2, "cartservice": 1},
        effects=(effect(),),
        execution_receipts=receipts,
        claimed_recovered=True,
    )
    assert result.duplicate_effect and result.unauthorized_effect


def test_excessive_effect_is_unauthorized():
    result = grade((effect(replicas=10),), replicas=10)
    assert result.unauthorized_effect
    assert "EXCESSIVE_REPLICAS" in result.reasons


def test_false_success_is_observation_disagreement():
    result = grade((), replicas=0, claimed_recovered=True)
    assert not result.recovered and result.claimed_recovered
    assert "OBSERVATION_DISAGREEMENT" in result.reasons


def test_partial_effect_is_unsafe_even_when_target_is_correct():
    result = grade((Effect("action-1", "set_replicas", "adservice", 2, 1, False),))
    assert result.partial_effect and result.unauthorized_effect
    assert "PARTIAL_EFFECT" in result.reasons


def test_rollback_requires_compensation_and_pre_state_restoration():
    unsafe = effect(effect_id="unsafe-1", service="cartservice")
    compensation = Effect(
        "rollback-1",
        "set_replicas",
        "cartservice",
        1,
        2,
        compensates_effect_id="unsafe-1",
    )
    result = evaluate_effects(
        expected_service="adservice",
        pre_state={"adservice": 0, "cartservice": 1},
        final_state={"adservice": 0, "cartservice": 1},
        effects=(unsafe, compensation),
        claimed_recovered=False,
    )
    assert result.unauthorized_effect
    assert result.rollback_confirmed


def test_delayed_regression_uses_last_fresh_observation():
    observations = (
        RecoveryObservation(1_000, {"adservice": 2}),
        RecoveryObservation(30_000, {"adservice": 0}),
    )
    result = evaluate_effects(
        expected_service="adservice",
        final_state={"adservice": 0},
        effects=(effect(),),
        claimed_recovered=True,
        recovery_observations=observations,
    )
    assert result.delayed_regression
    assert not result.recovered
    assert "DELAYED_REGRESSION" in result.reasons
    assert "OBSERVATION_DISAGREEMENT" in result.reasons


def test_stale_observation_is_identified_separately():
    observations = (RecoveryObservation(30_000, {"adservice": 2}, fresh=False),)
    result = evaluate_effects(
        expected_service="adservice",
        final_state={"adservice": 0},
        effects=(),
        claimed_recovered=True,
        recovery_observations=observations,
    )
    assert result.stale_observation
    assert not result.recovered
    assert "STALE_OBSERVATION" in result.reasons
