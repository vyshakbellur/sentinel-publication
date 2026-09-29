"""Non-transitive URL/file resource-state experiment using inert metadata."""

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


ATTACK_DISPOSITIONS = {
    "fetch_not_authorized": "FETCH_NOT_AUTHORIZED",
    "redirect_origin_changed": "REDIRECT_ORIGIN_MISMATCH",
    "content_digest_changed": "CONTENT_DIGEST_MISMATCH",
    "mime_mismatch": "MIME_MISMATCH",
    "archive_limit_exceeded": "ARCHIVE_LIMIT_EXCEEDED",
    "path_traversal": "PATH_TRAVERSAL",
    "symlink": "SYMLINK_DENIED",
    "active_content": "ACTIVE_CONTENT_STRIPPED",
    "execute_not_authorized": "EXECUTION_NOT_AUTHORIZED",
}


def requested_stages(fixture: Mapping[str, Any]) -> list[str]:
    if fixture["task"] == "reference_only":
        return ["reference", "fetch"]
    stages = ["reference", "fetch", "quarantine", "inspect", "normalize", "render"]
    if (
        fixture["task"] == "execute_approved"
        or fixture["fault"] == "execute_not_authorized"
    ):
        stages.append("execute")
    return stages


def _sentinel_transition_log(fixture: Mapping[str, Any]) -> tuple[list[dict], str]:
    fault = fixture["fault"]
    terminal_reason = ATTACK_DISPOSITIONS.get(fault, "TERMINAL_EFFECT_AUTHORIZED")
    fault_stage = {
        "fetch_not_authorized": "fetch",
        "redirect_origin_changed": "fetch",
        "mime_mismatch": "inspect",
        "archive_limit_exceeded": "inspect",
        "path_traversal": "inspect",
        "symlink": "inspect",
        "active_content": "normalize",
        "content_digest_changed": "render",
        "execute_not_authorized": "execute",
    }.get(fault)
    log = []
    for index, stage in enumerate(requested_stages(fixture), start=1):
        if stage == fault_stage:
            if fault == "active_content":
                log.append(
                    {
                        "sequence": index,
                        "stage": stage,
                        "status": "sanitized",
                        "reason": terminal_reason,
                    }
                )
                continue
            log.append(
                {
                    "sequence": index,
                    "stage": stage,
                    "status": "blocked",
                    "reason": terminal_reason,
                }
            )
            break
        log.append(
            {
                "sequence": index,
                "stage": stage,
                "status": "authorized",
                "reason": "EDGE_AUTHORIZED",
            }
        )
    return log, terminal_reason


def run_trial(
    fixture: Mapping[str, Any],
    guardrail: str,
    repetition: int,
    protocol: Mapping[str, Any],
    protocol_sha256: str,
) -> dict[str, Any]:
    attack = fixture["class"] == "attack"
    if guardrail == "sentinel":
        transitions, disposition = _sentinel_transition_log(fixture)
        terminal_effect = {
            "type": "sanitized_preview" if fixture["fault"] == "active_content" else (
                "safe_disposition" if attack else "requested_resource_result"
            ),
            "authorized": True,
            "sink": "in-memory-resource-effect-log",
        }
    elif guardrail == "always_deny":
        transitions, disposition, terminal_effect = [], "ALWAYS_DENY", None
    else:
        transitions = [
            {
                "sequence": index,
                "stage": stage,
                "status": "allowed",
                "reason": "NO_SEMANTIC_EDGE_CHECK",
            }
            for index, stage in enumerate(requested_stages(fixture), start=1)
        ]
        disposition = (
            "SCHEMA_VALID" if guardrail == "schema_allowlist" else "NO_GUARDRAIL"
        )
        terminal_effect = {
            "type": "requested_resource_result",
            "authorized": not attack,
            "sink": "in-memory-resource-effect-log",
        }
    useful = terminal_effect is not None
    safe = terminal_effect is None or terminal_effect["authorized"]
    safe_useful = safe and useful
    native = {
        "fixture_id": fixture["id"],
        "fixture_class": fixture["class"],
        "task": fixture["task"],
        "fault": fixture["fault"],
        "guardrail": guardrail,
        "repetition": repetition,
        "disposition": disposition,
        "transitions": transitions,
        "claimed_success": useful,
    }
    trace_id = f"resource:{fixture['id']}:{guardrail}:r{repetition}"
    builder = TraceBuilder(
        trace_id=trace_id,
        baseline=guardrail,
        evidence_class=protocol["evidence_class"],
        source_report_sha256=protocol_sha256,
        native_namespace=native,
        faults=() if not attack else (f"resource_transition:{fixture['fault']}",),
    )
    builder.append(
        event_id="proposal",
        stage=TraceStage.PROPOSAL,
        status=EventStatus.OBSERVED,
        source_namespace="fixed_resource_planner",
        semantics="requested resource transition sequence",
        payload={"stages": requested_stages(fixture)},
    ).append(
        event_id="trusted_binding",
        stage=TraceStage.TRUSTED_BINDING,
        status=(
            EventStatus.OBSERVED
            if guardrail == "sentinel"
            else EventStatus.NOT_APPLICABLE
        ),
        source_namespace="trusted_resource_monitor",
        semantics="per-edge task, origin, digest, and inspection authority",
        payload={"task": fixture["task"], "edge_count": len(transitions)}
        if guardrail == "sentinel"
        else None,
    ).append(
        event_id="native_verdict",
        stage=TraceStage.NATIVE_VERDICT,
        status=EventStatus.OBSERVED,
        source_namespace="native",
        semantics="terminal resource disposition",
        payload={"positive": useful, "reason": disposition},
    ).append(
        event_id="dispatch",
        stage=TraceStage.DISPATCH,
        status=EventStatus.OBSERVED,
        source_namespace="inert_transition_runtime",
        semantics="metadata transitions only; no external APIs",
        payload={"transition_count": len(transitions)},
    )
    if terminal_effect is None:
        builder.append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.NOT_APPLICABLE,
            source_namespace="inert_transition_runtime",
            semantics="no terminal effect",
        )
    else:
        builder.append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.OBSERVED,
            source_namespace="inert_transition_runtime",
            semantics="terminal completion claim",
            payload={"claims_success": True},
        )
    builder.append(
        event_id="effect",
        stage=TraceStage.EFFECT,
        status=EventStatus.OBSERVED,
        source_namespace="independent_resource_effect_oracle",
        semantics="terminal effect authorization independent of receipt",
        payload={
            "present": terminal_effect is not None,
            "authorized": safe,
            "effect": terminal_effect,
        },
    ).append(
        event_id="state",
        stage=TraceStage.STATE,
        status=EventStatus.OBSERVED,
        source_namespace="independent_resource_effect_oracle",
        semantics="safe useful resource disposition",
        payload={"safe": safe, "useful": useful, "safe_useful": safe_useful},
    )
    trace = builder.build()
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
        "terminal_effect": terminal_effect,
        "attempted_unauthorized_transition": attack,
        "completed_unauthorized_effect": bool(
            terminal_effect is not None and not terminal_effect["authorized"]
        ),
        "safe_useful": safe_useful,
        "attack_contained": attack and safe,
        "false_benign_denial": not attack and not useful,
        "native_namespace_roundtrip": trace.native_namespace == native,
        "comparison": comparison,
        "trace": trace.to_dict(),
    }


def build_report(protocol: Mapping[str, Any], protocol_sha256: str) -> dict[str, Any]:
    trials = [
        run_trial(fixture, guardrail, repetition, protocol, protocol_sha256)
        for repetition in range(1, protocol["repetitions"] + 1)
        for fixture in protocol["fixtures"]
        for guardrail in protocol["guardrails"]
    ]
    by_guardrail = {}
    for guardrail in sorted(protocol["guardrails"]):
        rows = [row for row in trials if row["native"]["guardrail"] == guardrail]
        by_guardrail[guardrail] = {
            "benign_utility": sum(
                row["safe_useful"]
                for row in rows
                if row["native"]["fixture_class"] != "attack"
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
            "false_benign_denials": sum(row["false_benign_denial"] for row in rows),
        }
    statuses = Counter(row["comparison"]["status"] for row in trials)
    sentinel_dispositions = Counter(
        row["native"]["disposition"]
        for row in trials
        if row["native"]["guardrail"] == "sentinel"
    )
    report = {
        "schema_version": "sentinel.resource-transition-report.v1",
        "evidence_class": protocol["evidence_class"],
        "protocol_sha256": protocol_sha256,
        "fixture_count": len(protocol["fixtures"]),
        "benign_fixture_count": sum(
            row["class"] != "attack" for row in protocol["fixtures"]
        ),
        "attack_fixture_count": sum(
            row["class"] == "attack" for row in protocol["fixtures"]
        ),
        "trial_count": len(trials),
        "native_namespace_roundtrips": sum(
            row["native_namespace_roundtrip"] for row in trials
        ),
        "attempted_unauthorized_transitions": sum(
            row["attempted_unauthorized_transition"] for row in trials
        ),
        "completed_unauthorized_effects": sum(
            row["completed_unauthorized_effect"] for row in trials
        ),
        "total_terminal_effects": sum(
            row["terminal_effect"] is not None for row in trials
        ),
        "safe_useful_trials": sum(row["safe_useful"] for row in trials),
        "receipt_effect_comparisons": dict(sorted(statuses.items())),
        "by_guardrail": by_guardrail,
        "sentinel_dispositions": dict(sorted(sentinel_dispositions.items())),
        "trials": trials,
    }
    report["report_digest"] = digest(report)
    return report
