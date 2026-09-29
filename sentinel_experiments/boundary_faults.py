"""Cross-layer fault injection and minimal assurance cut-set analysis."""

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


ADAPTER = "sentinel_adapter_fault"
BROKER = "sentinel_broker_fault"
OBSERVER = "sentinel_observer_fault"
FIDES_ADAPTER = "fides_mislabeled_adapter_reconstruction"


def _is_minimal(candidates: list[frozenset[str]], item: frozenset[str]) -> bool:
    return not any(other < item for other in candidates)


def _minimal_cut_sets(
    condition_rows: Mapping[frozenset[str], list[Mapping[str, Any]]],
    outcome_field: str,
) -> list[list[str]]:
    failing = [
        faults
        for faults, rows in condition_rows.items()
        if faults and any(bool(row[outcome_field]) for row in rows)
    ]
    minimal = [faults for faults in failing if _is_minimal(failing, faults)]
    return [sorted(faults) for faults in sorted(minimal, key=lambda x: (len(x), sorted(x)))]


def _trial(
    *,
    seed: Mapping[str, Any],
    attack: bool,
    condition: Mapping[str, Any],
    protocol: Mapping[str, Any],
    protocol_sha256: str,
) -> dict[str, Any]:
    family = condition["family"]
    faults = frozenset(condition["faults"])
    adapter_fault = ADAPTER in faults or FIDES_ADAPTER in faults
    broker_fault = BROKER in faults
    observer_fault = OBSERVER in faults

    if not attack:
        admitted = family != "always_deny"
    elif family == "none":
        admitted = True
    elif family == "always_deny":
        admitted = False
    else:
        admitted = adapter_fault

    dispatched_unauthorized = attack and (admitted or broker_fault)
    if family == "always_deny":
        effect = None
    elif dispatched_unauthorized:
        effect = {
            "type": "unauthorized_consequence",
            "consequence": seed["consequence"],
            "authorized": False,
            "sink": "in-memory-boundary-fault-effect-log",
        }
    else:
        effect = {
            "type": "benign_task_completion" if not attack else "safe_block_notice",
            "authorized": True,
            "sink": "in-memory-boundary-fault-effect-log",
        }

    unauthorized = bool(effect and not effect["authorized"])
    useful = effect is not None
    safe_useful = useful and not unauthorized
    observer_available = family == "sentinel"
    observer_detected = observer_available and unauthorized and not observer_fault
    silent_unauthorized = observer_available and unauthorized and not observer_detected
    native = {
        "seed_id": seed["id"],
        "seed_class": "attack" if attack else "benign",
        "condition": condition["id"],
        "family": family,
        "faults": sorted(faults),
        "adapter_admitted": admitted,
        "broker_dispatched_unauthorized": dispatched_unauthorized,
        "claimed_success": useful,
    }
    trace = (
        TraceBuilder(
            trace_id=f"boundary:{seed['id']}:{condition['id']}",
            baseline=condition["id"],
            evidence_class=protocol["evidence_class"],
            source_report_sha256=protocol_sha256,
            native_namespace=native,
            faults=sorted(faults),
        )
        .append(
            event_id="proposal",
            stage=TraceStage.PROPOSAL,
            status=EventStatus.OBSERVED,
            source_namespace="fixed_development_action",
            semantics="identical inert action across fault conditions",
            payload={"seed_id": seed["id"], "attack": attack},
        )
        .append(
            event_id="trusted_binding",
            stage=TraceStage.TRUSTED_BINDING,
            status=EventStatus.OBSERVED,
            source_namespace="adapter",
            semantics="adapter authority decision under declared faults",
            payload={"admitted": admitted, "faulted": adapter_fault},
        )
        .append(
            event_id="native_verdict",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="reference-monitor decision",
            payload={"positive": admitted},
        )
        .append(
            event_id="dispatch",
            stage=TraceStage.DISPATCH,
            status=EventStatus.OBSERVED,
            source_namespace="credential_broker",
            semantics="broker dispatch under declared faults",
            payload={
                "submitted": effect is not None,
                "unauthorized_submission": dispatched_unauthorized,
                "faulted": broker_fault,
            },
        )
        .append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.OBSERVED if effect else EventStatus.NOT_APPLICABLE,
            source_namespace="inert_boundary_runtime",
            semantics="terminal completion claim",
            payload={"claims_success": True} if effect else None,
        )
        .append(
            event_id="system_observer",
            stage=TraceStage.EFFECT,
            status=(EventStatus.OBSERVED if observer_available else EventStatus.NOT_APPLICABLE),
            source_namespace="sentinel_system_observer",
            semantics="system-level unauthorized-effect alarm",
            payload={
                "detected_unauthorized": observer_detected,
                "faulted": observer_fault,
            }
            if observer_available
            else None,
        )
        .append(
            event_id="independent_effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED,
            source_namespace="independent_research_oracle",
            semantics="actual consequence independent of native and system observer",
            payload={
                "present": effect is not None,
                "unauthorized": unauthorized,
                "effect": effect,
            },
        )
        .append(
            event_id="state",
            stage=TraceStage.STATE,
            status=EventStatus.OBSERVED,
            source_namespace="independent_research_oracle",
            semantics="safe useful and silent-compromise state",
            payload={
                "safe_useful": safe_useful,
                "silent_unauthorized": silent_unauthorized,
            },
        )
        .build()
    )
    receipt_comparison = compare_boolean_fields(
        trace,
        comparison_id="receipt_success_vs_safe_useful_effect",
        left_event_id="receipt",
        left_field="claims_success",
        right_event_id="state",
        right_field="safe_useful",
    )
    observer_comparison = compare_boolean_fields(
        trace,
        comparison_id="system_observer_vs_independent_unauthorized_effect",
        left_event_id="system_observer",
        left_field="detected_unauthorized",
        right_event_id="independent_effect",
        right_field="unauthorized",
    )
    return {
        "trial_id": trace.trace_id,
        "native": native,
        "effect": effect,
        "completed_unauthorized_effect": unauthorized,
        "safe_useful": safe_useful,
        "observer_available": observer_available,
        "observer_detected_unauthorized": observer_detected,
        "silent_unauthorized_effect": silent_unauthorized,
        "receipt_comparison": receipt_comparison,
        "observer_comparison": observer_comparison,
        "native_namespace_roundtrip": trace.native_namespace == native,
        "trace": trace.to_dict(),
    }


def build_report(protocol: Mapping[str, Any], protocol_sha256: str) -> dict[str, Any]:
    trials = [
        _trial(
            seed=seed,
            attack=attack,
            condition=condition,
            protocol=protocol,
            protocol_sha256=protocol_sha256,
        )
        for condition in protocol["conditions"]
        for attack, seeds in (
            (True, protocol["attack_seeds"]),
            (False, protocol["benign_seeds"]),
        )
        for seed in seeds
    ]
    by_condition = {}
    for condition in protocol["conditions"]:
        rows = [row for row in trials if row["native"]["condition"] == condition["id"]]
        attacks = [row for row in rows if row["native"]["seed_class"] == "attack"]
        benign = [row for row in rows if row["native"]["seed_class"] == "benign"]
        by_condition[condition["id"]] = {
            "benign_utility": sum(row["safe_useful"] for row in benign),
            "safe_attack_utility": sum(row["safe_useful"] for row in attacks),
            "unauthorized_effects": sum(
                row["completed_unauthorized_effect"] for row in attacks
            ),
            "detected_unauthorized_effects": sum(
                row["observer_detected_unauthorized"] for row in attacks
            ),
            "silent_unauthorized_effects": sum(
                row["silent_unauthorized_effect"] for row in attacks
            ),
        }

    sentinel_fault_rows: dict[frozenset[str], list[Mapping[str, Any]]] = {}
    for condition in protocol["conditions"]:
        if condition["family"] != "sentinel":
            continue
        faults = frozenset(condition["faults"])
        sentinel_fault_rows[faults] = [
            row
            for row in trials
            if row["native"]["condition"] == condition["id"]
            and row["native"]["seed_class"] == "attack"
        ]
    receipt_statuses = Counter(row["receipt_comparison"]["status"] for row in trials)
    observer_statuses = Counter(row["observer_comparison"]["status"] for row in trials)
    report = {
        "schema_version": "sentinel.boundary-fault-cutsets-report.v1",
        "evidence_class": protocol["evidence_class"],
        "protocol_sha256": protocol_sha256,
        "trial_count": len(trials),
        "attack_trials": sum(row["native"]["seed_class"] == "attack" for row in trials),
        "benign_trials": sum(row["native"]["seed_class"] == "benign" for row in trials),
        "completed_unauthorized_effects": sum(row["completed_unauthorized_effect"] for row in trials),
        "safe_useful_trials": sum(row["safe_useful"] for row in trials),
        "terminal_effects": sum(row["effect"] is not None for row in trials),
        "receipt_effect_comparisons": dict(sorted(receipt_statuses.items())),
        "observer_effect_comparisons": dict(sorted(observer_statuses.items())),
        "sentinel_detected_unauthorized_effects": sum(
            row["observer_detected_unauthorized"] for row in trials
        ),
        "sentinel_silent_unauthorized_effects": sum(
            row["silent_unauthorized_effect"] for row in trials
        ),
        "fides_mislabeled_unauthorized_effects": by_condition[
            "fides_mislabeled_adapter_reconstruction"
        ]["unauthorized_effects"],
        "minimal_sentinel_prevention_cut_sets": _minimal_cut_sets(
            sentinel_fault_rows, "completed_unauthorized_effect"
        ),
        "minimal_sentinel_silent_cut_sets": _minimal_cut_sets(
            sentinel_fault_rows, "silent_unauthorized_effect"
        ),
        "by_condition": by_condition,
        "confirmatory_holdouts_evaluated": 0,
        "trials": trials,
    }
    report["report_digest"] = digest(report)
    return report
