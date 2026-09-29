"""Execute deterministic boundary-fault probes against the pinned ToolGate artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _revision(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    args = _args()
    source = args.source.resolve()
    protocol_path = args.protocol.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing evidence: {output}")

    protocol = json.loads(protocol_path.read_text())
    actual_revision = _revision(source)
    expected_revision = protocol["source"]["revision"]
    if actual_revision != expected_revision:
        raise SystemExit(
            f"ToolGate revision mismatch: expected {expected_revision}, got {actual_revision}"
        )

    sys.path.insert(0, str(source))
    from toolgate.contracts import Postcondition, Precondition, ToolContract
    from toolgate.core import ToolExecutor
    from toolgate.pipeline import Action, ToolGatePipeline

    fixture = protocol["fixture"]
    approved = fixture["approved_destination"]
    substituted = fixture["substituted_destination"]

    class FixedRetriever:
        def retrieve(self, query: str, state_summary: str = "", top_k: int = 25):
            return [fixture["tool_name"]]

    def make_reasoner():
        calls = 0

        def reasoner(query, history, state):
            nonlocal calls
            calls += 1
            if calls == 1:
                return Action(type="start_call_tool", content="send notification")
            return Action(type="answer", content="done")

        return reasoner

    rows: list[dict[str, Any]] = []
    for scenario in protocol["scenarios"]:
        destination = approved if scenario["destination"] == "approved" else substituted
        effects: list[str] = []

        def execute(tool_name: str, params: dict[str, Any], tool_config=None):
            behavior = scenario["executor_behavior"]
            if behavior in {"effect_and_valid_result", "effect_and_malformed_result"}:
                effects.append(params["destination"])
            if behavior == "effect_and_malformed_result":
                return dict(fixture["malformed_result"])
            return dict(fixture["valid_result"])

        if scenario["guardrail"] == "no_defense":
            result = execute(fixture["tool_name"], {"destination": destination})
            native_accept = None
            state_committed = None
            trace = []
        else:
            if scenario["guardrail"] == "always_deny":
                precondition = Precondition(check_function=lambda state: False)
            elif scenario["guardrail"] == "toolgate_unparsed_equality":
                precondition = Precondition(
                    constraints=["destination == approved_destination"]
                )
            else:
                precondition = Precondition(constraints=["exists(destination)"])

            contract = ToolContract(
                tool_name=fixture["tool_name"],
                tool_description="Send a notification to a destination",
                precondition=precondition,
                postcondition=Postcondition(
                    result_constraints=['has_field("receipt")'],
                    state_update_rules={"receipt": "result.receipt"},
                ),
                input_schema={
                    "type": "object",
                    "properties": {"destination": {"type": "string"}},
                    "required": ["destination"],
                },
                output_schema={
                    "type": "object",
                    "properties": {"receipt": {"type": "string"}},
                    "required": ["receipt"],
                },
            )
            pipeline = ToolGatePipeline(
                tool_contracts={fixture["tool_name"]: contract},
                llm_reasoner=make_reasoner(),
                tool_executor=ToolExecutor(tool_executor_func=execute),
                retriever=FixedRetriever(),
                max_steps=2,
            )
            result = pipeline.run(
                query="Send the approved notification",
                initial_entities={
                    "destination": (destination, "string"),
                    "approved_destination": (approved, "string"),
                },
            )
            trace = result["trace"]
            attempted = [item for item in trace if item["tool_called"] is not None]
            native_accept = bool(
                attempted and attempted[-1]["verification_result"]["success"]
            )
            state_committed = "receipt" in result["final_state"]

        effect = bool(effects)
        unauthorized_effect = any(value != approved for value in effects)
        expected = protocol["acceptance"][scenario["id"]]
        observed = {
            "native_accept": native_accept,
            "effect": effect,
            "unauthorized_effect": unauthorized_effect,
        }
        rows.append(
            {
                "scenario": scenario["id"],
                "guardrail": scenario["guardrail"],
                "destination": destination,
                "native": {
                    "accepted_and_committed": native_accept,
                    "symbolic_state_committed": state_committed,
                    "trace": trace,
                },
                "independent": {
                    "effect_observed": effect,
                    "effect_destinations": effects,
                    "unauthorized_effect": unauthorized_effect,
                    "verdict_effect_disagreement": (
                        native_accept is not None and native_accept != effect
                    ),
                },
                "matches_preregistered": observed == expected,
            }
        )

    summary = {
        "scenarios": len(rows),
        "matched_preregistered": sum(row["matches_preregistered"] for row in rows),
        "native_effect_disagreements": sum(
            row["independent"]["verdict_effect_disagreement"] for row in rows
        ),
        "unauthorized_effects": sum(
            row["independent"]["unauthorized_effect"] for row in rows
        ),
    }
    report = {
        "schema_version": "sentinel.toolgate-artifact-fault-probe.v1",
        "evidence_class": protocol["evidence_class"],
        "toolgate_revision": actual_revision,
        "protocol_sha256": _digest(protocol_path),
        "summary": summary,
        "accepted": summary["matched_preregistered"] == len(rows),
        "rows": rows,
        "limitations": protocol["limitations"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"accepted": report["accepted"], "summary": summary}, indent=2))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
