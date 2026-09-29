"""Post-development synthetic challenge set with explicit validity downgrade."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from .action_effect_trace import (
    EventStatus,
    TraceBuilder,
    TraceStage,
    compare_boolean_fields,
)
from .contracts import digest


def _trial(
    case: Mapping[str, Any],
    defense: str,
    protocol: Mapping[str, Any],
    protocol_sha256: str,
) -> dict[str, Any]:
    duplicate_case = case["factor"] == "execution_effect_correspondence"
    always_deny = defense == "always_deny"
    boundary_defense = defense in {"fides_correct_label_reconstruction", "sentinel"}
    prevented = boundary_defense and not duplicate_case

    if always_deny:
        effect = None
        reason = "ALWAYS_DENY"
    elif prevented:
        effect = {
            "type": "safe_requested_task_completion",
            "authorized": True,
            "effect_count": 1,
            "sink": "in-memory-prospective-challenge-log",
        }
        reason = (
            case["sentinel_disposition"]
            if defense == "sentinel"
            else case["fides_disposition"]
        )
    else:
        effect = {
            "type": "unauthorized_consequence",
            "authorized": False,
            "effect_count": 2 if duplicate_case else 1,
            "attempted_effect": case["attempted_effect"],
            "sink": "in-memory-prospective-challenge-log",
        }
        reason = (
            case["sentinel_disposition"]
            if defense == "sentinel"
            else case["fides_disposition"]
            if defense == "fides_correct_label_reconstruction"
            else "PLAN_ADMITTED"
        )

    unauthorized = bool(effect and not effect["authorized"])
    safe_useful = bool(effect and effect["authorized"])
    observer_available = defense == "sentinel"
    observer_detected = observer_available and unauthorized
    native = {
        "case_id": case["id"],
        "factor": case["factor"],
        "defense": defense,
        "reason": reason,
        "claimed_success": effect is not None,
    }
    trace = (
        TraceBuilder(
            trace_id=f"prospective:{case['id']}:{defense}",
            baseline=defense,
            evidence_class=protocol["evidence_class"],
            source_report_sha256=protocol_sha256,
            native_namespace=native,
            faults=(case["factor"],),
        )
        .append(
            event_id="proposal",
            stage=TraceStage.PROPOSAL,
            status=EventStatus.OBSERVED,
            source_namespace="postdevelopment_frozen_case",
            semantics="synthetic challenge action",
            payload={
                "request": case["request"],
                "attempted_effect": case["attempted_effect"],
            },
        )
        .append(
            event_id="native_verdict",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="defense-family outcome",
            payload={"positive": effect is not None, "reason": reason},
        )
        .append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.OBSERVED if effect else EventStatus.NOT_APPLICABLE,
            source_namespace="inert_challenge_runtime",
            semantics="terminal completion claim",
            payload={"claims_success": True} if effect else None,
        )
        .append(
            event_id="system_observer",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED if observer_available else EventStatus.NOT_APPLICABLE,
            source_namespace="sentinel_system_observer",
            semantics="system-level unauthorized-effect alarm",
            payload={"detected_unauthorized": observer_detected}
            if observer_available
            else None,
        )
        .append(
            event_id="independent_effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED,
            source_namespace="independent_research_oracle",
            semantics="actual effect independent of native result",
            payload={"unauthorized": unauthorized, "effect": effect},
        )
        .append(
            event_id="state",
            stage=TraceStage.STATE,
            status=EventStatus.OBSERVED,
            source_namespace="independent_research_oracle",
            semantics="safe useful completion",
            payload={"safe_useful": safe_useful},
        )
        .build()
    )
    return {
        "trial_id": trace.trace_id,
        "native": native,
        "effect": effect,
        "completed_unauthorized_effect": unauthorized,
        "safe_useful": safe_useful,
        "observer_detected_unauthorized": observer_detected,
        "receipt_comparison": compare_boolean_fields(
            trace,
            comparison_id="receipt_success_vs_safe_useful_effect",
            left_event_id="receipt",
            left_field="claims_success",
            right_event_id="state",
            right_field="safe_useful",
        ),
        "observer_comparison": compare_boolean_fields(
            trace,
            comparison_id="system_observer_vs_independent_unauthorized_effect",
            left_event_id="system_observer",
            left_field="detected_unauthorized",
            right_event_id="independent_effect",
            right_field="unauthorized",
        ),
        "native_namespace_roundtrip": trace.native_namespace == native,
        "trace": trace.to_dict(),
    }


def build_report(protocol: Mapping[str, Any], protocol_sha256: str) -> dict[str, Any]:
    trials = [
        _trial(case, defense, protocol, protocol_sha256)
        for case in protocol["cases"]
        for defense in protocol["defenses"]
    ]
    by_defense = {}
    for defense in sorted(protocol["defenses"]):
        rows = [row for row in trials if row["native"]["defense"] == defense]
        by_defense[defense] = {
            "safe_useful": sum(row["safe_useful"] for row in rows),
            "unauthorized_effects": sum(
                row["completed_unauthorized_effect"] for row in rows
            ),
            "detected_unauthorized_effects": sum(
                row["observer_detected_unauthorized"] for row in rows
            ),
        }
    receipt_statuses = Counter(row["receipt_comparison"]["status"] for row in trials)
    observer_statuses = Counter(row["observer_comparison"]["status"] for row in trials)
    sentinel = by_defense["sentinel"]
    fides = by_defense["fides_correct_label_reconstruction"]
    report = {
        "schema_version": "sentinel.prospective-challenge-matrix-report.v1",
        "evidence_class": protocol["evidence_class"],
        "protocol_sha256": protocol_sha256,
        "confirmatory_validity": protocol["confirmatory_validity"],
        "frozen_identifier_cases_evaluated": len(protocol["cases"]),
        "valid_confirmatory_holdouts_evaluated": 0,
        "trial_count": len(trials),
        "completed_unauthorized_effects": sum(
            row["completed_unauthorized_effect"] for row in trials
        ),
        "safe_useful_trials": sum(row["safe_useful"] for row in trials),
        "terminal_effects": sum(row["effect"] is not None for row in trials),
        "receipt_effect_comparisons": dict(sorted(receipt_statuses.items())),
        "observer_effect_comparisons": dict(sorted(observer_statuses.items())),
        "sentinel_cases_passed": sentinel["safe_useful"],
        "sentinel_cases_failed": sentinel["unauthorized_effects"],
        "sentinel_detected_but_not_prevented": sentinel[
            "detected_unauthorized_effects"
        ],
        "fides_cases_passed": fides["safe_useful"],
        "fides_cases_failed": fides["unauthorized_effects"],
        "by_defense": by_defense,
        "uncertainty_interval": None,
        "uncertainty_interval_reason": (
            "Five purposively constructed deterministic cases are not random or "
            "exchangeable observations."
        ),
        "trials": trials,
    }
    report["report_digest"] = digest(report)
    return report
