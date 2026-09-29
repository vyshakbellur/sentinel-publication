"""Normalize selected baseline evidence without modifying native namespaces."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from sentinel_experiments.action_effect_trace import (
    EventStatus,
    TraceBuilder,
    TraceStage,
    compare_boolean_fields,
)
from sentinel_experiments.contracts import digest


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_verified(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = root / spec["path"]
    actual = _sha256(path)
    if actual != spec["sha256"]:
        raise SystemExit(
            "evidence hash mismatch for "
            f"{path}: expected {spec['sha256']}, got {actual}"
        )
    return json.loads(path.read_text())


def _missing_stages(builder: TraceBuilder) -> TraceBuilder:
    return (
        builder.append(
            event_id="proposal",
            stage=TraceStage.PROPOSAL,
            status=EventStatus.NOT_OBSERVED,
            source_namespace="adapter",
            semantics="source report does not retain the model proposal",
        )
        .append(
            event_id="normalized_action",
            stage=TraceStage.NORMALIZED_ACTION,
            status=EventStatus.NOT_OBSERVED,
            source_namespace="adapter",
            semantics="source report does not retain a complete normalized action",
        )
    )


def _camel_trace(report: dict[str, Any], source_hash: str, case_id: str):
    row = next(item for item in report["observations"] if item["case_id"] == case_id)
    call = row["tool_calls"][0]
    builder = TraceBuilder(
        trace_id=f"camel:{case_id}",
        baseline="CaMeL",
        evidence_class=report["evidence_class"],
        source_report_sha256=source_hash,
        native_namespace=row,
    )
    builder.append(
        event_id="proposal",
        stage=TraceStage.PROPOSAL,
        status=EventStatus.NOT_OBSERVED,
        source_namespace="adapter",
        semantics="the deterministic policy probe does not contain an LLM proposal",
    ).append(
        event_id="normalized_action",
        stage=TraceStage.NORMALIZED_ACTION,
        status=EventStatus.OBSERVED,
        source_namespace="native.tool_calls",
        semantics="released CaMeL tool call recorded by the probe",
        payload={"operation": call["function"], "arguments": call["args"]},
    ).append(
        event_id="trusted_binding",
        stage=TraceStage.TRUSTED_BINDING,
        status=EventStatus.OBSERVED,
        source_namespace="sentinel_probe",
        semantics="probe provenance and preregistered authorization expectation",
        payload={
            "resource_id": row["resource_id"],
            "resource_provenance": row["resource_provenance"],
            "authorized": row["sentinel_expected"] == "allow",
        },
    ).append(
        event_id="native_verdict",
        stage=TraceStage.NATIVE_VERDICT,
        status=EventStatus.OBSERVED,
        source_namespace="native",
        semantics="CaMeL operation-specific policy decision",
        payload={"positive": row["observed_decision"] == "allow"},
    ).append(
        event_id="dispatch",
        stage=TraceStage.DISPATCH,
        status=EventStatus.OBSERVED,
        source_namespace="native.tool_calls",
        semantics="presence of the recorded tool call",
        payload={"submitted": bool(row["tool_calls"])},
    ).append(
        event_id="receipt",
        stage=TraceStage.RECEIPT,
        status=EventStatus.NOT_OBSERVED,
        source_namespace="adapter",
        semantics="probe report does not retain a separate execution receipt",
    ).append(
        event_id="effect",
        stage=TraceStage.EFFECT,
        status=EventStatus.OBSERVED,
        source_namespace="independent",
        semantics="fresh-state benchmark mutation oracle",
        payload={"completed": row["effect_observed"]},
    )
    trace = builder.build()
    comparisons = [
        compare_boolean_fields(
            trace,
            comparison_id="trusted_authority_vs_effect",
            left_event_id="trusted_binding",
            left_field="authorized",
            right_event_id="effect",
            right_field="completed",
        ),
        compare_boolean_fields(
            trace,
            comparison_id="native_verdict_vs_effect",
            left_event_id="native_verdict",
            left_field="positive",
            right_event_id="effect",
            right_field="completed",
        ),
    ]
    return trace, comparisons, row


def _agent_c_trace(report: dict[str, Any], source_hash: str, replay_id: str):
    native = report["dynamic_replays"][replay_id]
    builder = _missing_stages(
        TraceBuilder(
            trace_id=f"agent-c:{replay_id}",
            baseline="Agent-C",
            evidence_class=report["evidence_class"],
            source_report_sha256=source_hash,
            native_namespace=native,
        )
    )
    builder.append(
        event_id="trusted_binding",
        stage=TraceStage.TRUSTED_BINDING,
        status=EventStatus.OBSERVED,
        source_namespace="sentinel_static_audit",
        semantics="identity is confirmation-bound while the selected value is not",
        payload={"identity_bound": True, "complete_tuple_bound": False},
    ).append(
        event_id="native_verdict",
        stage=TraceStage.NATIVE_VERDICT,
        status=EventStatus.OBSERVED,
        source_namespace="native",
        semantics="released formula admission for the alternate allowed reason",
        payload={"positive": native["alternate_allowed_reason"]},
    )
    for event_id, stage in (
        ("dispatch", TraceStage.DISPATCH),
        ("receipt", TraceStage.RECEIPT),
        ("effect", TraceStage.EFFECT),
    ):
        builder.append(
            event_id=event_id,
            stage=stage,
            status=EventStatus.NOT_OBSERVED,
            source_namespace="adapter",
            semantics="model-free formula replay does not execute the domain tool",
        )
    trace = builder.build()
    comparisons = [
        compare_boolean_fields(
            trace,
            comparison_id="native_verdict_vs_effect",
            left_event_id="native_verdict",
            left_field="positive",
            right_event_id="effect",
            right_field="completed",
        )
    ]
    return trace, comparisons, native


def _fides_trace(
    report: dict[str, Any], source_hash: str, guardrail: str, injection_task: str
):
    row = next(
        item
        for item in report["rows"]
        if item["guardrail"] == guardrail
        and item["injection_task"] == injection_task
    )
    builder = _missing_stages(
        TraceBuilder(
            trace_id=f"fides:{guardrail}:{injection_task}",
            baseline="Fides reconstruction",
            evidence_class=report["evidence_class"],
            source_report_sha256=source_hash,
            native_namespace=row,
            faults=("adapter.integrity_mislabel",),
        )
    )
    builder.append(
        event_id="trusted_binding",
        stage=TraceStage.TRUSTED_BINDING,
        status=EventStatus.OBSERVED,
        source_namespace="reconstruction",
        semantics="integrity label assigned to the attack ground-truth trace",
        payload={"assigned_integrity": row["assigned_attack_integrity"]},
    ).append(
        event_id="native_verdict",
        stage=TraceStage.NATIVE_VERDICT,
        status=EventStatus.OBSERVED,
        source_namespace="native.agentdojo",
        semantics="AgentDojo attack-goal result retained without modification",
        payload={"positive": row["native"]["attack_goal_achieved"]},
    ).append(
        event_id="dispatch",
        stage=TraceStage.DISPATCH,
        status=EventStatus.OBSERVED,
        source_namespace="independent",
        semantics="required attack write call executed by the reconstruction",
        payload={
            "submitted": row["independent"]["exact_attack_write_executed"]
        },
    ).append(
        event_id="receipt",
        stage=TraceStage.RECEIPT,
        status=EventStatus.NOT_OBSERVED,
        source_namespace="adapter",
        semantics="reconstruction report does not retain a separate receipt",
    ).append(
        event_id="effect",
        stage=TraceStage.EFFECT,
        status=EventStatus.OBSERVED,
        source_namespace="independent",
        semantics="exact released attack write execution indicator",
        payload={
            "completed": row["independent"]["exact_attack_write_executed"]
        },
    )
    trace = builder.build()
    comparisons = [
        compare_boolean_fields(
            trace,
            comparison_id="native_verdict_vs_effect",
            left_event_id="native_verdict",
            left_field="positive",
            right_event_id="effect",
            right_field="completed",
        ),
        compare_boolean_fields(
            trace,
            comparison_id="dispatch_vs_effect",
            left_event_id="dispatch",
            left_field="submitted",
            right_event_id="effect",
            right_field="completed",
        ),
    ]
    return trace, comparisons, row


def _toolgate_trace(report: dict[str, Any], source_hash: str, scenario: str):
    row = next(item for item in report["rows"] if item["scenario"] == scenario)
    native_trace = row["native"]["trace"]
    first_call = next(
        (item for item in native_trace if item["tool_called"] is not None), None
    )
    baseline = {
        "no_defense_substitution": "no-defense",
        "always_deny_valid": "always-deny",
    }.get(scenario, "ToolGate")
    builder = TraceBuilder(
        trace_id=f"{baseline.lower()}:{scenario}",
        baseline=baseline,
        evidence_class=report["evidence_class"],
        source_report_sha256=source_hash,
        native_namespace=row,
        faults=(
            ("executor.false_success",)
            if scenario == "toolgate_lying_success"
            else ()
        ),
    )
    builder.append(
        event_id="proposal",
        stage=TraceStage.PROPOSAL,
        status=(EventStatus.OBSERVED if native_trace else EventStatus.NOT_OBSERVED),
        source_namespace="native",
        semantics="deterministic reasoner action retained by the ToolGate probe",
        payload=(
            {"content": native_trace[0]["action_content"]} if native_trace else None
        ),
    ).append(
        event_id="normalized_action",
        stage=TraceStage.NORMALIZED_ACTION,
        status=EventStatus.OBSERVED,
        source_namespace="probe",
        semantics="fixture tool and destination supplied to the selected condition",
        payload={"operation": "SendNotification", "destination": row["destination"]},
    ).append(
        event_id="trusted_binding",
        stage=TraceStage.TRUSTED_BINDING,
        status=EventStatus.NOT_OBSERVED,
        source_namespace="adapter",
        semantics="native row does not expose an authenticated authority tuple",
    )
    native_accept = row["native"]["accepted_and_committed"]
    builder.append(
        event_id="native_verdict",
        stage=TraceStage.NATIVE_VERDICT,
        status=(
            EventStatus.NOT_APPLICABLE
            if native_accept is None
            else EventStatus.OBSERVED
        ),
        source_namespace="native",
        semantics="ToolGate postcondition acceptance and symbolic-state commitment",
        payload=({"positive": native_accept} if native_accept is not None else None),
    ).append(
        event_id="dispatch",
        stage=TraceStage.DISPATCH,
        status=EventStatus.OBSERVED,
        source_namespace="native",
        semantics="tool invocation presence in the released pipeline trace or control",
        payload={
            "submitted": (
                bool(first_call)
                if scenario != "no_defense_substitution"
                else row["independent"]["effect_observed"]
            )
        },
    )
    if first_call and first_call["tool_result"] is not None:
        builder.append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.OBSERVED,
            source_namespace="native.tool_result",
            semantics="well-formed fixture receipt returned by the executor",
            payload={"claims_completion": True, "value": first_call["tool_result"]},
        )
    else:
        builder.append(
            event_id="receipt",
            stage=TraceStage.RECEIPT,
            status=EventStatus.NOT_OBSERVED,
            source_namespace="adapter",
            semantics="selected row does not retain a tool receipt",
        )
    builder.append(
        event_id="effect",
        stage=TraceStage.EFFECT,
        status=EventStatus.OBSERVED,
        source_namespace="independent",
        semantics="isolated in-memory delivery sink",
        payload={"completed": row["independent"]["effect_observed"]},
    )
    trace = builder.build()
    comparisons = [
        compare_boolean_fields(
            trace,
            comparison_id="native_verdict_vs_effect",
            left_event_id="native_verdict",
            left_field="positive",
            right_event_id="effect",
            right_field="completed",
        ),
        compare_boolean_fields(
            trace,
            comparison_id="dispatch_vs_effect",
            left_event_id="dispatch",
            left_field="submitted",
            right_event_id="effect",
            right_field="completed",
        ),
    ]
    if scenario == "toolgate_lying_success":
        comparisons.append(
            compare_boolean_fields(
                trace,
                comparison_id="receipt_vs_effect",
                left_event_id="receipt",
                left_field="claims_completion",
                right_event_id="effect",
                right_field="completed",
            )
        )
    return trace, comparisons, row


def main() -> int:
    args = _args()
    root = args.repository.resolve()
    protocol_path = args.protocol.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing evidence: {output}")
    protocol = json.loads(protocol_path.read_text())
    reports = {
        name: _load_verified(root, spec)
        for name, spec in protocol["source_reports"].items()
    }
    hashes = {
        name: spec["sha256"] for name, spec in protocol["source_reports"].items()
    }
    selected = protocol["selections"]
    built = [
        _camel_trace(reports["camel"], hashes["camel"], selected["camel_case"]),
        _agent_c_trace(
            reports["agent_c"], hashes["agent_c"], selected["agent_c_replay"]
        ),
        _fides_trace(
            reports["fides"],
            hashes["fides"],
            selected["fides_guardrail"],
            selected["fides_injection_task"],
        ),
    ]
    built.extend(
        _toolgate_trace(reports["toolgate"], hashes["toolgate"], scenario)
        for scenario in selected["toolgate_scenarios"]
    )

    records = []
    all_comparisons = []
    native_roundtrips = 0
    for trace, comparisons, source_native in built:
        trace.validate()
        trace_payload = trace.to_dict()
        native_roundtrips += trace_payload["native_namespace"] == source_native
        records.append(
            {
                "trace": trace_payload,
                "sentinel_comparisons": comparisons,
                "comparison_digest": digest(comparisons),
            }
        )
        all_comparisons.extend(
            {**comparison, "trace_id": trace.trace_id}
            for comparison in comparisons
        )

    counts = Counter(item["status"] for item in all_comparisons)
    lookup = {
        f"{item['trace_id']}:{item['comparison_id']}": item["status"]
        for item in all_comparisons
    }
    expected = protocol["acceptance"]
    summary = {
        "trace_count": len(records),
        "valid_hash_chains": len(records),
        "native_namespace_roundtrips": native_roundtrips,
        "comparison_status_counts": dict(sorted(counts.items())),
    }
    acceptance_checks = {
        "trace_count": summary["trace_count"] == expected["trace_count"],
        "valid_hash_chains": summary["valid_hash_chains"]
        == expected["valid_hash_chains"],
        "native_namespace_roundtrips": summary["native_namespace_roundtrips"]
        == expected["native_namespace_roundtrips"],
        "comparison_status_counts": summary["comparison_status_counts"]
        == expected["comparison_status_counts"],
        "required_comparisons": all(
            lookup.get(key) == value
            for key, value in expected["required_comparisons"].items()
        ),
    }
    report = {
        "schema_version": "sentinel.action-effect-trace-validation.v1",
        "protocol_sha256": _sha256(protocol_path),
        "summary": summary,
        "acceptance_checks": acceptance_checks,
        "accepted": all(acceptance_checks.values()),
        "records": records,
        "invariants": protocol["invariants"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"accepted": report["accepted"], "summary": summary}, indent=2))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
