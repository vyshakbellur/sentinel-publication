import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
SUBSET = json.loads(
    (ROOT / "experiments/protocol/agentdojo_development_subset.json").read_text()
)


def test_agentdojo_development_subset_is_frozen_and_development_only():
    assert SUBSET["status"] == "frozen-before-defense-outcomes"
    assert SUBSET["artifact"] == {
        "repository": "https://github.com/ethz-spylab/agentdojo",
        "revision": "928bbae820a89556b03de5cf818eb350cd6082d1",
        "release": "v0.1.34",
        "benchmark_version": "v1.2",
        "reason": (
            "CaMeL f083b6b locks AgentDojo 0.1.34 and calls benchmark "
            "version v1.2."
        ),
    }
    assert "Development-only" in SUBSET["selection"]["purpose"]
    assert not SUBSET["attack"]["adaptive_tuning_allowed"]


def test_agentdojo_subset_counts_and_ids_are_consistent():
    suites = SUBSET["selection"]["suites"]
    users = sum(len(suite["user_tasks"]) for suite in suites.values())
    injections = sum(len(suite["injection_tasks"]) for suite in suites.values())
    pairs = sum(
        len(suite["user_tasks"]) * len(suite["injection_tasks"])
        for suite in suites.values()
    )
    assert users == SUBSET["selection"]["selected_user_tasks"] == 16
    assert injections == SUBSET["selection"]["selected_injection_tasks"] == 16
    assert pairs == SUBSET["selection"]["adversarial_pairs"] == 64
    for suite in suites.values():
        assert len(suite["user_tasks"]) == len(set(suite["user_tasks"]))
        assert len(suite["injection_tasks"]) == len(set(suite["injection_tasks"]))


def test_known_scorer_disagreement_is_inside_the_frozen_subset():
    suites = SUBSET["selection"]["suites"]
    disagreements = SUBSET["selection"]["known_native_scorer_disagreements"]
    assert len(disagreements) == 1
    item = disagreements[0]
    assert item["user_task"] in suites[item["suite"]]["user_tasks"]
    assert item["injection_task"] in suites[item["suite"]]["injection_tasks"]
    assert SUBSET["metric_contract"]["explicit_alias"] == "attack_goal_achieved"
