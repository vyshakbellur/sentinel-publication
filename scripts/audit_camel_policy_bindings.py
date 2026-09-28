"""Validate and summarize CaMeL workspace attribute-policy coverage."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camel-source", type=Path, required=True)
    parser.add_argument("--agentdojo-source", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _revision(source: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registered_policy_tools(policy_path: Path) -> list[str]:
    tree = ast.parse(policy_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
            and target.attr == "policies"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, ast.List):
            continue
        tools: list[str] = []
        for element in node.value.elts:
            if not isinstance(element, ast.Tuple) or not element.elts:
                raise ValueError("unexpected policy registration entry")
            tool = ast.literal_eval(element.elts[0])
            if not isinstance(tool, str):
                raise ValueError("policy tool name is not a string")
            tools.append(tool)
        return tools
    raise ValueError("WorkspaceSecurityPolicyEngine.policies not found")


def main() -> int:
    args = _args()
    camel_source = args.camel_source.resolve()
    agentdojo_source = args.agentdojo_source.resolve()
    protocol_path = args.protocol.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing evidence: {output}")

    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    artifact = protocol["artifact"]
    actual_revisions = {
        "camel_revision": _revision(camel_source),
        "agentdojo_revision": _revision(agentdojo_source),
    }
    for key, actual in actual_revisions.items():
        if actual != artifact[key]:
            raise SystemExit(
                f"{key} mismatch: expected {artifact[key]}, got {actual}"
            )

    policy_path = (
        camel_source
        / "src/camel/pipeline_elements/security_policies/workspace.py"
    )
    policy_hash = _sha256(policy_path)
    if policy_hash != artifact["policy_source_sha256"]:
        raise SystemExit("workspace policy source hash mismatch")

    sys.path.insert(0, str(camel_source / "src"))
    sys.path.insert(0, str(agentdojo_source / "src"))
    from agentdojo.task_suite import get_suite

    suite = get_suite(artifact["benchmark_version"], artifact["suite"])
    tools_by_name = {tool.name: tool for tool in suite.tools}
    registered = _registered_policy_tools(policy_path)
    audited = list(protocol["operations"])
    if set(registered) != set(audited):
        raise SystemExit(
            f"policy inventory mismatch: registered={registered}, audited={audited}"
        )

    rows: list[dict[str, Any]] = []
    mode_counts: Counter[str] = Counter()
    authority_mode_counts: Counter[str] = Counter()
    authority_roles = set(protocol["authority_roles"])
    complete_operations: list[str] = []
    for operation, operation_spec in protocol["operations"].items():
        runtime_fields = list(tools_by_name[operation].parameters.model_fields)
        declared_fields = list(operation_spec["fields"])
        if runtime_fields != declared_fields:
            raise SystemExit(
                f"field inventory mismatch for {operation}: "
                f"runtime={runtime_fields}, declared={declared_fields}"
            )
        authority_fields: list[str] = []
        strictly_bound_fields: list[str] = []
        for field, field_spec in operation_spec["fields"].items():
            mode = field_spec["mode"]
            role = field_spec["role"]
            if mode not in protocol["mode_definitions"]:
                raise SystemExit(f"unknown mode {mode} for {operation}.{field}")
            mode_counts[mode] += 1
            if role in authority_roles:
                authority_fields.append(field)
                authority_mode_counts[mode] += 1
                if mode == "trusted_integrity":
                    strictly_bound_fields.append(field)
            rows.append(
                {
                    "operation": operation,
                    "field": field,
                    "role": role,
                    "mode": mode,
                }
            )
        if authority_fields and authority_fields == strictly_bound_fields:
            complete_operations.append(operation)

    authority_total = sum(authority_mode_counts.values())
    strict_total = authority_mode_counts["trusted_integrity"]
    report = {
        "schema_version": "sentinel.camel-policy-binding-audit-report.v1",
        "evidence_class": "version-validated-static-policy-audit",
        **actual_revisions,
        "benchmark_version": artifact["benchmark_version"],
        "suite": artifact["suite"],
        "policy_source_sha256": policy_hash,
        "protocol_sha256": _sha256(protocol_path),
        "registered_policy_tools": registered,
        "rows": rows,
        "summary": {
            "side_effect_operations": len(audited),
            "external_parameters": len(rows),
            "mode_counts_all_parameters": dict(sorted(mode_counts.items())),
            "authority_bearing_parameters": authority_total,
            "authority_mode_counts": dict(sorted(authority_mode_counts.items())),
            "strictly_trusted_authority_parameters": strict_total,
            "strict_authority_coverage": strict_total / authority_total,
            "fully_strictly_bound_operations": complete_operations,
            "fully_strictly_bound_operation_count": len(complete_operations),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=False)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
