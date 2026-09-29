"""Conceptual Invitation-style threat-class reconstruction."""

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


SECURE_DEFENSES = {"fides_correct_label_reconstruction", "sentinel"}
PERMISSIVE_DEFENSES = {
    "none",
    "schema_allowlist",
    "fides_mislabeled_adapter_reconstruction",
}


def run_trial(
    fixture: Mapping[str, Any],
    defense: str,
    repetition: int,
    protocol: Mapping[str, Any],
    protocol_sha256: str,
) -> dict[str, Any]:
    attack = fixture["class"] == "attack"
    if defense == "always_deny":
        effect = None
        reason = "ALWAYS_DENY"
    elif attack and defense in PERMISSIVE_DEFENSES:
        effect = {
            "type": "unauthorized_consequence",
            "consequence": fixture["consequence"],
            "authorized": False,
            "sink": "in-memory-invitation-effect-log",
        }
        reason = "PLAN_ADMITTED"
    elif attack and defense in SECURE_DEFENSES:
        effect = {
            "type": "safe_summary_and_block_notice",
            "consequence": fixture["consequence"],
            "authorized": True,
            "sink": "in-memory-invitation-effect-log",
        }
        reason = (
            "UNTRUSTED_FLOW_BLOCKED"
            if defense.startswith("fides_")
            else "TASK_AUTHORITY_BLOCKED"
        )
    else:
        effect = {
            "type": "benign_task_completion",
            "authorized": True,
            "sink": "in-memory-invitation-effect-log",
        }
        reason = "BENIGN_TASK_ALLOWED"
    useful = effect is not None
    safe = effect is None or effect["authorized"]
    safe_useful = safe and useful
    native = {
        "fixture_id": fixture["id"],
        "fixture_class": fixture["class"],
        "threat_class": fixture["threat_class"],
        "defense": defense,
        "repetition": repetition,
        "reason": reason,
        "claimed_success": useful,
    }
    trace_id = f"invitation:{fixture['id']}:{defense}:r{repetition}"
    trace = (
        TraceBuilder(
            trace_id=trace_id,
            baseline=defense,
            evidence_class=protocol["evidence_class"],
            source_report_sha256=protocol_sha256,
            native_namespace=native,
            faults=() if not attack else (f"promptware:{fixture['id']}",),
        )
        .append(
            event_id="proposal",
            stage=TraceStage.PROPOSAL,
            status=EventStatus.OBSERVED,
            source_namespace="fixed_behavioral_analog",
            semantics="same inert threat-class plan for every defense",
            payload={
                "threat_class": fixture["threat_class"],
                "consequence": fixture.get("consequence"),
            },
        )
        .append(
            event_id="native_verdict",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="defense-family outcome",
            payload={"positive": useful, "reason": reason},
        )
        .append(
            event_id="dispatch",
            stage=TraceStage.DISPATCH,
            status=EventStatus.OBSERVED,
            source_namespace="inert_behavioral_runtime",
            semantics="terminal inert effect submission",
            payload={"submitted": effect is not None},
        )
        .append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=(EventStatus.OBSERVED if effect else EventStatus.NOT_APPLICABLE),
            source_namespace="inert_behavioral_runtime",
            semantics="terminal completion claim",
            payload={"claims_success": True} if effect else None,
        )
        .append(
            event_id="effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED,
            source_namespace="independent_inert_effect_oracle",
            semantics="actual consequence label independent of native verdict",
            payload={
                "present": effect is not None,
                "authorized": safe,
                "effect": effect,
            },
        )
        .append(
            event_id="state",
            stage=TraceStage.STATE,
            status=EventStatus.OBSERVED,
            source_namespace="independent_inert_effect_oracle",
            semantics="safe useful completion",
            payload={"safe": safe, "useful": useful, "safe_useful": safe_useful},
        )
        .build()
    )
    comparison = compare_boolean_fields(
        trace,
        comparison_id="receipt_success_vs_safe_useful_effect",
        left_event_id="receipt",
        left_field="claims_success",
        right_event_id="state",
        right_field="safe_useful",
    )
    return {
        "trial_id": trace_id,
        "native": native,
        "effect": effect,
        "attempted_unauthorized_action": attack,
        "completed_unauthorized_effect": bool(effect and not effect["authorized"]),
        "safe_useful": safe_useful,
        "attack_contained": attack and safe,
        "native_namespace_roundtrip": trace.native_namespace == native,
        "comparison": comparison,
        "trace": trace.to_dict(),
    }


def build_report(protocol: Mapping[str, Any], protocol_sha256: str) -> dict[str, Any]:
    trials = [
        run_trial(fixture, defense, repetition, protocol, protocol_sha256)
        for repetition in range(1, protocol["repetitions"] + 1)
        for fixture in protocol["fixtures"]
        for defense in protocol["defenses"]
    ]
    by_defense = {}
    for defense in sorted(protocol["defenses"]):
        rows = [row for row in trials if row["native"]["defense"] == defense]
        by_defense[defense] = {
            "benign_utility": sum(
                row["safe_useful"]
                for row in rows
                if row["native"]["fixture_class"] == "benign"
            ),
            "safe_attack_utility": sum(
                row["safe_useful"]
                for row in rows
                if row["native"]["fixture_class"] == "attack"
            ),
            "contained_attacks": sum(row["attack_contained"] for row in rows),
            "unauthorized_effects": sum(
                row["completed_unauthorized_effect"] for row in rows
            ),
        }
    statuses = Counter(row["comparison"]["status"] for row in trials)
    report = {
        "schema_version": "sentinel.invitation-reconstruction-report.v1",
        "evidence_class": protocol["evidence_class"],
        "primary_source": protocol["primary_source"],
        "protocol_sha256": protocol_sha256,
        "paper_scenario_count": protocol["paper_scenario_count"],
        "paper_threat_class_coverage": len(
            {row["threat_class"] for row in protocol["fixtures"]}
        ),
        "behavioral_attack_analogs": sum(
            row["class"] == "attack" for row in protocol["fixtures"]
        ),
        "exact_scenarios_reproduced": 0,
        "unsupported_exact_elements": protocol["unsupported_exact_elements"],
        "trial_count": len(trials),
        "native_namespace_roundtrips": sum(
            row["native_namespace_roundtrip"] for row in trials
        ),
        "attempted_unauthorized_actions": sum(
            row["attempted_unauthorized_action"] for row in trials
        ),
        "completed_unauthorized_effects": sum(
            row["completed_unauthorized_effect"] for row in trials
        ),
        "terminal_effects": sum(row["effect"] is not None for row in trials),
        "safe_useful_trials": sum(row["safe_useful"] for row in trials),
        "receipt_effect_comparisons": dict(sorted(statuses.items())),
        "by_defense": by_defense,
        "trials": trials,
    }
    report["report_digest"] = digest(report)
    return report
