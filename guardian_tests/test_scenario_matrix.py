"""Release tests for the 375-context authorization scenario matrix."""

from __future__ import annotations

import json
from collections import Counter

from guardian.benchmark.scenario_matrix import (
    build_context_scenarios,
    get_scenario_templates,
)
from guardian.layers.progressive_cost import GuardianConfig, validate_request
from guardian.talk_experiments.real_experiments import (
    _unexpected_decision_counts,
    run_experiment_progressive_cost,
)


def test_matrix_has_six_complete_matched_pairs_and_declared_outcomes():
    templates = get_scenario_templates()
    assert len(templates) == 12
    assert len({item["scenario_id"] for item in templates}) == 12

    pairs = {}
    for item in templates:
        pairs.setdefault(item["pair_id"], set()).add(item["variant"])
    assert len(pairs) == 6
    assert all(variants == {"benign", "adversarial"} for variants in pairs.values())
    assert Counter(item["expected_decision"] for item in templates) == {
        "ALLOW": 6,
        "BLOCK": 4,
        "ESCALATE": 2,
    }


def test_template_oracles_match_both_modes_without_defining_each_other():
    for scenario in get_scenario_templates():
        observed = []
        for mode in ("full", "progressive"):
            result = validate_request(
                scenario["request"],
                scenario["user_permissions"],
                GuardianConfig(mode=mode),
            )
            observed.append(result.decision)
            assert result.decision == scenario["expected_decision"]
        assert observed[0] == observed[1]


def test_context_metadata_is_not_injected_into_guardian_request(tmp_path):
    case_dir = tmp_path / "re1ob_cartservice_cpu_1"
    case_dir.mkdir()
    (case_dir / "metrics.json").write_text(
        json.dumps({"cartservice_cpu": [[1, 1.0], [2, 2.0]]})
    )

    records = build_context_scenarios(case_dir)
    assert len(records) == 12
    assert all(record["context"]["used_for_guardian_decision"] is False for record in records)
    assert all(record["context"]["role"] == "contextual_metadata_only" for record in records)
    assert all("_telemetry" not in record["request"] for record in records)
    assert all("context" not in record["request"] for record in records)

    records[0]["request"]["tool_name"] = "changed"
    assert records[1]["request"]["tool_name"] != "changed"


def test_false_outcome_accounting_keeps_classes_separate():
    assert _unexpected_decision_counts("BLOCK", "ALLOW") == {
        "false_allow": 1,
        "false_block": 0,
        "false_escalate": 0,
    }
    assert _unexpected_decision_counts("ALLOW", "BLOCK") == {
        "false_allow": 0,
        "false_block": 1,
        "false_escalate": 0,
    }
    assert _unexpected_decision_counts("BLOCK", "ESCALATE") == {
        "false_allow": 0,
        "false_block": 0,
        "false_escalate": 1,
    }


def test_full_375_context_matrix_reports_declared_counts(tmp_path):
    for index in range(375):
        case_dir = tmp_path / f"re1ob_service_cpu_{index}"
        case_dir.mkdir()
        (case_dir / "metrics.json").write_text(
            json.dumps({"service_cpu": [[1, 1.0], [2, 2.0]]})
        )

    result = run_experiment_progressive_cost(str(tmp_path))

    assert result["independent_telemetry_contexts"] == 375
    assert result["scenario_templates"] == 12
    assert result["matched_boundary_pairs"] == 6
    assert result["case_scenario_evaluations_per_mode"] == 4_500
    assert result["pipeline_evaluations_across_both_modes"] == 9_000
    assert result["corpus_reused_between_modes"] is True
    assert result["oracle_source"] == (
        "declared_scenario_templates_not_observed_guardian_output"
    )
    assert result["context_role"] == (
        "contextual_metadata_only_not_used_for_guardian_decision"
    )
    assert result["full_mode"]["actual_decisions"] == {
        "ALLOW": 2_250,
        "BLOCK": 1_500,
        "ESCALATE": 750,
    }
    assert result["progressive_mode"]["actual_decisions"] == {
        "ALLOW": 2_250,
        "BLOCK": 1_500,
        "ESCALATE": 750,
    }
    for mode in ("full_mode", "progressive_mode"):
        assert result[mode]["oracle_matches"] == 4_500
        assert result[mode]["false_allow"] == 0
        assert result[mode]["false_block"] == 0
        assert result[mode]["false_escalate"] == 0

    assert result["decision_equivalence"] == {
        "equivalent": True,
        "mismatch_count": 0,
        "mismatches": [],
    }
    assert result["full_mode"]["verifier_calls"] == 3_000
    assert result["progressive_mode"]["verifier_calls"] == 1_500
    assert result["verifier_calls_avoided"] == 1_500
    assert len(result["per_template"]) == 12
