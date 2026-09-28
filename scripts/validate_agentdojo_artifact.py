"""Fail-closed validation of a pinned AgentDojo development subset."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _revision(source: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--subset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    subset_path = args.subset.resolve()
    subset = json.loads(subset_path.read_text(encoding="utf-8"))
    source = args.source.resolve()
    expected_revision = subset["artifact"]["revision"]
    actual_revision = _revision(source)
    if actual_revision != expected_revision:
        raise SystemExit(
            f"artifact revision mismatch: expected {expected_revision}, got {actual_revision}"
        )

    sys.path.insert(0, str(source / "src"))
    from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
    from agentdojo.attacks.baseline_attacks import DirectAttack
    from agentdojo.functions_runtime import FunctionsRuntime
    from agentdojo.task_suite import get_suites
    from agentdojo.task_suite.task_suite import is_task_injectable
    from agentdojo.types import get_text_content_as_str

    benchmark_version = subset["artifact"]["benchmark_version"]
    suites = get_suites(benchmark_version)
    suite_reports: dict[str, Any] = {}
    pair_results: list[dict[str, Any]] = []
    failures: list[str] = []
    expected_disagreements = {
        (item["suite"], item["user_task"], item["injection_task"])
        for item in subset["selection"].get("known_native_scorer_disagreements", [])
    }
    observed_disagreements: set[tuple[str, str, str]] = set()

    for suite_name, selected in subset["selection"]["suites"].items():
        suite = suites[suite_name]
        suite_valid, (user_checks, injection_checks) = suite.check(False)

        defaults = suite.get_injection_vector_defaults()
        canaries = {name: f"---CANARY_{name}---" for name in defaults}
        environment = suite.load_and_inject_default_environment(canaries)
        native_injectable = 0
        corrected_injectable = 0
        tool_content_types: dict[str, int] = {}
        for task in suite.user_tasks.values():
            pipeline = GroundTruthPipeline(task)
            _, _, _, messages, _ = pipeline.query(
                task.PROMPT,
                FunctionsRuntime(suite.tools),
                environment.model_copy(deep=True),
            )
            native_injectable += int(
                is_task_injectable(messages, list(canaries.values()))
            )
            outputs: list[str] = []
            for message in messages:
                if message["role"] != "tool":
                    continue
                content = message["content"]
                type_name = type(content).__name__
                tool_content_types[type_name] = tool_content_types.get(type_name, 0) + 1
                outputs.append(get_text_content_as_str(content))
            corrected_injectable += int(
                any(canary in " ".join(outputs) for canary in canaries.values())
            )

        selected_users = selected["user_tasks"]
        selected_injections = selected["injection_tasks"]
        unknown_users = sorted(set(selected_users) - set(suite.user_tasks))
        unknown_injections = sorted(
            set(selected_injections) - set(suite.injection_tasks)
        )
        if unknown_users or unknown_injections:
            failures.append(
                f"{suite_name}: unknown users={unknown_users}, injections={unknown_injections}"
            )
            continue
        selected_ground_truth_failures = [
            task_id for task_id in selected_users if not user_checks[task_id][0]
        ] + [
            task_id for task_id in selected_injections if not injection_checks[task_id]
        ]
        if selected_ground_truth_failures:
            failures.append(
                f"{suite_name}: selected ground truths failed "
                f"{selected_ground_truth_failures}"
            )

        for user_id in selected_users:
            user_task = suite.get_user_task_by_id(user_id)
            attack = DirectAttack(suite, GroundTruthPipeline(user_task))
            candidates = attack.get_injection_candidates(user_task)
            if not candidates:
                failures.append(f"{suite_name}/{user_id}: no injection candidates")
            for injection_id in selected_injections:
                injection_task = suite.get_injection_task_by_id(injection_id)
                injections = attack.attack(user_task, injection_task)
                benign = suite.run_task_with_pipeline(
                    GroundTruthPipeline(user_task),
                    user_task,
                    injection_task,
                    injections,
                )
                adversarial = suite.run_task_with_pipeline(
                    GroundTruthPipeline(injection_task),
                    user_task,
                    injection_task,
                    injections,
                )
                passed = benign == (True, False) and adversarial == (False, True)
                pair_key = (suite_name, user_id, injection_id)
                expected_disagreement = not passed and pair_key in expected_disagreements
                if not passed:
                    observed_disagreements.add(pair_key)
                if not passed and not expected_disagreement:
                    failures.append(
                        f"{suite_name}/{user_id}/{injection_id}: scorer sanity failed"
                    )
                pair_results.append(
                    {
                        "suite": suite_name,
                        "user_task": user_id,
                        "injection_task": injection_id,
                        "candidate_count": len(candidates),
                        "benign_ground_truth": {
                            "utility": benign[0],
                            "attack_goal_achieved": benign[1],
                        },
                        "injection_ground_truth": {
                            "utility": adversarial[0],
                            "attack_goal_achieved": adversarial[1],
                        },
                        "passed": passed,
                        "expected_native_scorer_disagreement": expected_disagreement,
                    }
                )

        suite_reports[suite_name] = {
            "released_ground_truth_check_passed": suite_valid,
            "user_ground_truths_passed": sum(value[0] for value in user_checks.values()),
            "user_ground_truths_total": len(user_checks),
            "injection_ground_truths_passed": sum(injection_checks.values()),
            "injection_ground_truths_total": len(injection_checks),
            "selected_ground_truths_passed": not selected_ground_truth_failures,
            "released_injectability_count": native_injectable,
            "representation_aware_injectability_count": corrected_injectable,
            "tool_content_types": tool_content_types,
        }

    expected_pairs = subset["selection"]["adversarial_pairs"]
    if len(pair_results) != expected_pairs:
        failures.append(
            f"expected {expected_pairs} scorer pairs, observed {len(pair_results)}"
        )
    missing_expected = expected_disagreements - observed_disagreements
    unexpected_declared = observed_disagreements - expected_disagreements
    if missing_expected:
        failures.append(f"declared scorer disagreements not observed: {sorted(missing_expected)}")
    if unexpected_declared:
        failures.append(f"undeclared scorer disagreements observed: {sorted(unexpected_declared)}")

    report: dict[str, Any] = {
        "schema_version": "sentinel.agentdojo-artifact-validation.v1",
        "artifact_revision": actual_revision,
        "benchmark_version": benchmark_version,
        "subset_sha256": _digest(subset_path),
        "evidence_class": subset["evidence_class"],
        "suite_reports": suite_reports,
        "scorer_pair_summary": {
            "total": len(pair_results),
            "native_sanity_passed": sum(result["passed"] for result in pair_results),
            "expected_native_scorer_disagreements": sum(
                result["expected_native_scorer_disagreement"]
                for result in pair_results
            ),
            "unexpected_failures": sum(
                not result["passed"]
                and not result["expected_native_scorer_disagreement"]
                for result in pair_results
            ),
        },
        "scorer_pairs": pair_results,
        "validation_failures": failures,
        "valid": not failures,
        "limitations": [
            "This validates released deterministic ground truths and scorers, "
            "not an LLM defense result.",
            "Dependencies are contemporary loose resolutions rather than the artifact lock.",
            "The development subset is excluded from later confirmatory tuning claims.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["scorer_pair_summary"], sort_keys=True))
    print(json.dumps({"valid": report["valid"], "failures": failures}, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
