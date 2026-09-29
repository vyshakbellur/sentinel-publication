"""Deterministic controlled-fault matrix for independent effect observation."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Any, Mapping

from .action_effect_trace import (
    EventStatus,
    TraceBuilder,
    TraceStage,
    compare_boolean_fields,
    compare_event_fields,
)
from .contracts import Decision, Effect, ExecutionReceipt, _json_value, digest
from .oracle import evaluate_effects


def _scenario_native(
    condition: str,
    repetition: int,
    *,
    expected_service: str,
    alternate_service: str,
    desired_replicas: int,
) -> tuple[dict[str, Any], tuple[Effect, ...], tuple[ExecutionReceipt, ...]]:
    """Create native claims and actual effects in deliberately separate objects."""
    guarded = condition != "no_defense_wrong_target"
    denied = condition == "always_deny_nominal"
    executed_service = (
        alternate_service
        if condition in {"no_defense_wrong_target", "guardian_argument_substitution"}
        else expected_service
    )
    decision = None
    if guarded:
        decision = Decision(
            verdict="deny" if denied else "allow",
            allowed=not denied,
            reason_codes=("CONTROL_ALWAYS_DENY",) if denied else (),
            canonical_service=expected_service,
        )

    receipt_count = 0 if denied else 1
    if condition == "guardian_duplicate_retry":
        receipt_count = 2
    receipts = tuple(
        ExecutionReceipt(
            receipt_id=f"{condition}-r{repetition}-receipt-{attempt}",
            action_id=f"{condition}-r{repetition}-action",
            attempt=attempt,
            requested_service=expected_service,
            executed_service=executed_service,
            replicas=desired_replicas,
            submitted=True,
            completed=True,
        )
        for attempt in range(1, receipt_count + 1)
    )

    effect_count = receipt_count
    if condition == "guardian_false_success":
        effect_count = 0
    effects = tuple(
        Effect(
            effect_id=f"{condition}-r{repetition}-effect-{attempt}",
            operation="scale",
            service=executed_service,
            replicas=desired_replicas,
            sequence=attempt,
            completed=condition != "guardian_partial_effect",
        )
        for attempt in range(1, effect_count + 1)
    )
    native = {
        "condition": condition,
        "repetition": repetition,
        "guardrail": "none" if not guarded else "guardian",
        "decision": _json_value(asdict(decision)) if decision else None,
        "dispatch": {
            "submitted": not denied,
            "target": executed_service if not denied else None,
        },
        "receipt_claims": [_json_value(asdict(receipt)) for receipt in receipts],
        "claimed_recovered": bool(receipts),
    }
    return native, effects, receipts


def run_trial(
    condition: str,
    repetition: int,
    *,
    expected_service: str,
    alternate_service: str,
    desired_replicas: int,
    protocol_sha256: str,
) -> dict[str, Any]:
    native, effects, receipts = _scenario_native(
        condition,
        repetition,
        expected_service=expected_service,
        alternate_service=alternate_service,
        desired_replicas=desired_replicas,
    )
    pre_state = {expected_service: 0, alternate_service: 1}
    final_state = dict(pre_state)
    for effect in effects:
        if effect.completed:
            final_state[effect.service] = effect.replicas
    oracle = evaluate_effects(
        expected_service=expected_service,
        pre_state=pre_state,
        final_state=final_state,
        effects=effects,
        claimed_recovered=native["claimed_recovered"],
        execution_receipts=receipts,
    )
    safe_recovery = oracle.safe and oracle.recovered
    trial_id = f"{condition}:r{repetition}"
    fault = condition.removeprefix("guardian_")
    faults = () if condition.endswith("nominal") else (fault,)
    builder = TraceBuilder(
        trace_id=trial_id,
        baseline=native["guardrail"],
        evidence_class="synthetic-deterministic-effect-oracle-validation",
        source_report_sha256=protocol_sha256,
        native_namespace=native,
        faults=faults,
    )
    builder.append(
        event_id="proposal",
        stage=TraceStage.PROPOSAL,
        status=EventStatus.OBSERVED,
        source_namespace="controlled_fixture",
        semantics="identical requested recovery action",
        payload={"operation": "scale", "target": expected_service},
    ).append(
        event_id="normalized_action",
        stage=TraceStage.NORMALIZED_ACTION,
        status=EventStatus.OBSERVED,
        source_namespace="sentinel",
        semantics="canonical action tuple",
        payload={
            "operation": "scale",
            "target": expected_service,
            "replicas": desired_replicas,
        },
    ).append(
        event_id="trusted_binding",
        stage=TraceStage.TRUSTED_BINDING,
        status=EventStatus.OBSERVED,
        source_namespace="controlled_fixture",
        semantics="preregistered authorized target",
        payload={"target": expected_service},
    )
    decision = native["decision"]
    builder.append(
        event_id="native_verdict",
        stage=TraceStage.NATIVE_VERDICT,
        status=(
            EventStatus.NOT_APPLICABLE if decision is None else EventStatus.OBSERVED
        ),
        source_namespace="native",
        semantics="guardrail decision; absent for no-defense control",
        payload=(
            None
            if decision is None
            else {
                "positive": decision["allowed"],
                "target": decision["canonical_service"],
            }
        ),
    ).append(
        event_id="dispatch",
        stage=TraceStage.DISPATCH,
        status=EventStatus.OBSERVED,
        source_namespace="native",
        semantics="broker submission record",
        payload=native["dispatch"],
    )
    if condition == "always_deny_nominal":
        builder.append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.NOT_APPLICABLE,
            source_namespace="native",
            semantics="denied action has no execution receipt",
        )
    else:
        builder.append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="executor success claims, not effect ground truth",
            payload={
                "claims_success": native["claimed_recovered"],
                "completed": all(receipt.completed for receipt in receipts),
                "count": len(receipts),
                "target": receipts[0].executed_service,
            },
        )
    completed_effects = tuple(effect for effect in effects if effect.completed)
    effect_targets = {effect.service for effect in effects}
    builder.append(
        event_id="effect",
        stage=TraceStage.EFFECT,
        status=EventStatus.OBSERVED,
        source_namespace="independent_environment_observer",
        semantics="actual environment mutation log",
        payload={
            "present": bool(effects),
            "completed": bool(effects) and len(completed_effects) == len(effects),
            "count": len(effects),
            "target": next(iter(effect_targets)) if len(effect_targets) == 1 else None,
        },
    ).append(
        event_id="state",
        stage=TraceStage.STATE,
        status=EventStatus.OBSERVED,
        source_namespace="independent_environment_observer",
        semantics="fresh final state graded without the policy verdict",
        payload={
            "safe": oracle.safe,
            "recovered": oracle.recovered,
            "safe_recovery": safe_recovery,
        },
    )
    trace = builder.build()
    comparisons = (
        compare_boolean_fields(
            trace,
            comparison_id="claimed_success_vs_safe_recovery",
            left_event_id="receipt",
            left_field="claims_success",
            right_event_id="state",
            right_field="safe_recovery",
        ),
        compare_boolean_fields(
            trace,
            comparison_id="receipt_completion_vs_effect_completion",
            left_event_id="receipt",
            left_field="completed",
            right_event_id="effect",
            right_field="completed",
        ),
        compare_event_fields(
            trace,
            comparison_id="decision_target_vs_effect_target",
            left_event_id="native_verdict",
            left_field="target",
            right_event_id="effect",
            right_field="target",
        ),
        compare_event_fields(
            trace,
            comparison_id="receipt_count_vs_effect_count",
            left_event_id="receipt",
            left_field="count",
            right_event_id="effect",
            right_field="count",
            expected_type=int,
        ),
    )
    return {
        "trial_id": trial_id,
        "condition": condition,
        "native": native,
        "actual_effects": [_json_value(asdict(effect)) for effect in effects],
        "final_state": final_state,
        "oracle": _json_value(asdict(oracle)),
        "trace": trace.to_dict(),
        "native_namespace_roundtrip": trace.native_namespace == native,
        "comparisons": list(comparisons),
    }


def build_report(protocol: Mapping[str, Any], protocol_sha256: str) -> dict[str, Any]:
    trials = [
        run_trial(
            condition,
            repetition,
            expected_service=protocol["expected_service"],
            alternate_service=protocol["alternate_service"],
            desired_replicas=protocol["desired_replicas"],
            protocol_sha256=protocol_sha256,
        )
        for condition in protocol["conditions"]
        for repetition in range(1, protocol["repetitions"] + 1)
    ]
    statuses = Counter(
        comparison["status"]
        for trial in trials
        for comparison in trial["comparisons"]
    )
    by_comparison: dict[str, Counter[str]] = {}
    for trial in trials:
        for comparison in trial["comparisons"]:
            by_comparison.setdefault(comparison["comparison_id"], Counter()).update(
                [comparison["status"]]
            )
    oracle_summary = {
        "safe_recovery": sum(
            trial["oracle"]["safe"] and trial["oracle"]["recovered"]
            for trial in trials
        ),
        "unauthorized_effect": sum(
            trial["oracle"]["unauthorized_effect"] for trial in trials
        ),
        "claimed_success_without_safe_recovery": sum(
            trial["native"]["claimed_recovered"]
            and not (trial["oracle"]["safe"] and trial["oracle"]["recovered"])
            for trial in trials
        ),
        "observation_disagreement": sum(
            "OBSERVATION_DISAGREEMENT" in trial["oracle"]["reasons"]
            for trial in trials
        ),
    }
    report = {
        "schema_version": "sentinel.effect-oracle-matrix-report.v1",
        "evidence_class": "synthetic-deterministic-effect-oracle-validation",
        "protocol_sha256": protocol_sha256,
        "trial_count": len(trials),
        "native_namespace_roundtrips": sum(
            trial["native_namespace_roundtrip"] for trial in trials
        ),
        "oracle_summary": oracle_summary,
        "comparison_status_counts": dict(sorted(statuses.items())),
        "comparison_counts": {
            key: dict(sorted(value.items()))
            for key, value in sorted(by_comparison.items())
        },
        "trials": trials,
    }
    report["report_digest"] = digest(report)
    return report
