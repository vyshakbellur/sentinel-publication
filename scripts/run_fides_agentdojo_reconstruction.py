"""Run a minimal, clearly labeled Fides-style AgentDojo reconstruction."""

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
    expected_revision = protocol["source"]["agentdojo_revision"]
    if actual_revision != expected_revision:
        raise SystemExit(
            f"AgentDojo revision mismatch: expected {expected_revision}, got {actual_revision}"
        )

    sys.path.insert(0, str(source / "src"))
    from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
    from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
    from agentdojo.agent_pipeline.tool_execution import tool_result_to_str
    from agentdojo.attacks.baseline_attacks import DirectAttack
    from agentdojo.task_suite import get_suites
    from agentdojo.types import (
        ChatAssistantMessage,
        ChatToolResultMessage,
        text_content_block_from_string,
    )

    side_effect_tools = frozenset(protocol["reconstruction"]["side_effect_tools"])

    class ReconstructedFidesPipeline(BasePipelineElement):
        """Ground-truth proposal source plus a two-level integrity monitor."""

        def __init__(self, task, guardrail: str, label: str):
            self.task = task
            self.guardrail = guardrail
            self.label = label
            self.executed_calls: list[dict[str, Any]] = []
            self.blocked_calls: list[dict[str, Any]] = []

        def _allow(self, function: str) -> bool:
            if self.guardrail == "always_deny":
                return False
            if self.guardrail == "fides_correct_label":
                return not (self.label == "untrusted" and function in side_effect_tools)
            if self.guardrail in {"no_defense", "fides_mislabeled_adapter"}:
                return True
            raise ValueError(f"unknown guardrail {self.guardrail}")

        def query(self, query, runtime, env, messages=(), extra_args=None):
            emitted = []
            complete = True
            for call in self.task.ground_truth(env):
                record = {"function": call.function, "args": dict(call.args)}
                if not self._allow(call.function):
                    self.blocked_calls.append(record)
                    complete = False
                    break
                result, error = runtime.run_function(
                    env, call.function, call.args, raise_on_error=True
                )
                self.executed_calls.append({**record, "error": error})
                emitted.append(
                    ChatAssistantMessage(
                        role="assistant",
                        tool_calls=[call],
                        content=[text_content_block_from_string("")],
                    )
                )
                emitted.append(
                    ChatToolResultMessage(
                        role="tool",
                        content=[text_content_block_from_string(tool_result_to_str(result))],
                        tool_call=call,
                        tool_call_id=None,
                        error=None,
                    )
                )
            final_output = self.task.GROUND_TRUTH_OUTPUT if complete else ""
            emitted.append(
                ChatAssistantMessage(
                    role="assistant",
                    content=[text_content_block_from_string(final_output)],
                    tool_calls=None,
                )
            )
            return query, runtime, env, [*messages, *emitted], extra_args or {}

    suite = get_suites(protocol["source"]["benchmark_version"])[
        protocol["selection"]["suite"]
    ]
    user_task = suite.get_user_task_by_id(protocol["selection"]["user_task"])
    rows: list[dict[str, Any]] = []
    for injection_id in protocol["selection"]["injection_tasks"]:
        injection_task = suite.get_injection_task_by_id(injection_id)
        attack = DirectAttack(suite, GroundTruthPipeline(user_task))
        injections = attack.attack(user_task, injection_task)
        for guardrail in protocol["guardrails"]:
            benign_pipeline = ReconstructedFidesPipeline(
                user_task, guardrail, "trusted"
            )
            benign = suite.run_task_with_pipeline(
                benign_pipeline,
                user_task,
                injection_task,
                injections,
            )
            attack_label = (
                "trusted" if guardrail == "fides_mislabeled_adapter" else "untrusted"
            )
            attack_pipeline = ReconstructedFidesPipeline(
                injection_task, guardrail, attack_label
            )
            adversarial = suite.run_task_with_pipeline(
                attack_pipeline,
                user_task,
                injection_task,
                injections,
            )
            required_writes = [
                call.function
                for call in injection_task.ground_truth(
                    suite.load_and_inject_default_environment(injections)
                )
                if call.function in side_effect_tools
            ]
            executed_writes = [
                call["function"]
                for call in attack_pipeline.executed_calls
                if call["function"] in side_effect_tools
            ]
            rows.append(
                {
                    "user_task": user_task.ID,
                    "injection_task": injection_id,
                    "guardrail": guardrail,
                    "assigned_attack_integrity": attack_label,
                    "native": {
                        "benign_utility": benign[0],
                        "benign_attack_goal_achieved": benign[1],
                        "utility_under_attack_trace": adversarial[0],
                        "attack_goal_achieved": adversarial[1],
                    },
                    "independent": {
                        "required_attack_write_calls": required_writes,
                        "executed_attack_write_calls": executed_writes,
                        "exact_attack_write_executed": bool(required_writes)
                        and executed_writes == required_writes,
                        "blocked_calls": attack_pipeline.blocked_calls,
                    },
                }
            )

    summary: dict[str, Any] = {}
    for guardrail in protocol["guardrails"]:
        items = [row for row in rows if row["guardrail"] == guardrail]
        summary[guardrail] = {
            "pairs": len(items),
            "benign_utility_passes": sum(
                row["native"]["benign_utility"] for row in items
            ),
            "native_benign_attack_goals_achieved": sum(
                row["native"]["benign_attack_goal_achieved"] for row in items
            ),
            "native_attack_goals_achieved": sum(
                row["native"]["attack_goal_achieved"] for row in items
            ),
            "independent_exact_attack_writes_executed": sum(
                row["independent"]["exact_attack_write_executed"] for row in items
            ),
        }

    expected = protocol["acceptance"]
    acceptance_checks = {
        guardrail: {
            "benign_utility": summary[guardrail]["benign_utility_passes"]
            == (len(protocol["selection"]["injection_tasks"]) if values["benign_utility"] else 0),
            "attack_goals": summary[guardrail]["native_attack_goals_achieved"]
            == values["attack_goals_achieved"],
            "native_independent_attack_agreement": summary[guardrail][
                "native_attack_goals_achieved"
            ]
            == summary[guardrail]["independent_exact_attack_writes_executed"],
            "benign_trace_does_not_satisfy_attack": summary[guardrail][
                "native_benign_attack_goals_achieved"
            ]
            == 0,
        }
        for guardrail, values in expected.items()
    }
    report = {
        "schema_version": "sentinel.fides-agentdojo-reconstruction.v1",
        "evidence_class": protocol["evidence_class"],
        "agentdojo_revision": actual_revision,
        "protocol_sha256": _digest(protocol_path),
        "summary": summary,
        "acceptance_checks": acceptance_checks,
        "accepted": all(
            all(checks.values()) for checks in acceptance_checks.values()
        ),
        "rows": rows,
        "limitations": protocol["limitations"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"summary": summary, "accepted": report["accepted"]}, indent=2, sort_keys=True))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
