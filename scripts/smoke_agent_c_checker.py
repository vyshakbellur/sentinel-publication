"""Run a model-free smoke test over the pinned Agent-C checker artifact."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _digest(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_tool_specs(path: Path) -> list[dict[str, Any]]:
    module_spec = importlib.util.spec_from_file_location(path.stem, path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load specification module: {path}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.tool_specs


def main() -> int:
    args = _args()
    artifact_root = args.artifact_root.resolve()
    archive = args.archive.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing evidence: {output}")

    expected_md5 = "e37f84c00035d7d254170e474e938424"
    archive_md5 = _digest(archive, "md5")
    if archive_md5 != expected_md5:
        raise SystemExit(
            f"archive checksum mismatch: expected {expected_md5}, got {archive_md5}"
        )

    checker_dir = artifact_root / "src/tau2/agent/checker"
    sys.path.insert(0, str(checker_dir))
    from agc_checker import AgentCChecker
    from parsers import AgentCSpecParser

    released_spec_counts: dict[str, int] = {}
    empty_spec_counts: dict[str, int] = {}
    parse_failures: list[dict[str, str]] = []
    parser = AgentCSpecParser()
    for domain in ("retail", "airline", "telecom"):
        spec_path = (
            artifact_root
            / "src/tau2/agent/agentc_spec"
            / f"agentc_specs_{domain}.py"
        )
        tool_specs = _load_tool_specs(spec_path)
        released_spec_counts[domain] = len(tool_specs)
        empty_spec_counts[domain] = 0
        for index, tool_spec in enumerate(tool_specs):
            if not tool_spec["spec"].strip():
                # AgentCChecker.add_spec treats an empty string as an
                # intentionally unconstrained tool and returns true.
                empty_spec_counts[domain] += 1
                continue
            try:
                # Syntax-only validation intentionally avoids inventing the
                # runtime tool-type dictionary normally built by AgentC from
                # the fully installed tau2 domain schemas.
                parser.parser.parse(tool_spec["spec"])
            except Exception as exc:
                parse_failures.append(
                    {
                        "domain": domain,
                        "index": str(index),
                        "tool": tool_spec.get("tool", "<missing>"),
                        "exception_type": type(exc).__name__,
                        "exception_text": str(exc),
                    }
                )

    synthetic_spec = (
        "before(delete(resource_id=r1), True, "
        "authorize(resource_id=r2), r2 == r1)"
    )
    tool_types = {
        "delete": {"resource_id": "string"},
        "authorize": {"resource_id": "string"},
    }

    def check_with_trace(trace: list[dict[str, Any]], resource_id: str) -> bool:
        checker = AgentCChecker(env_type="synthetic")
        if not checker.add_tools(tool_types):
            raise RuntimeError("failed to register synthetic tool signatures")
        if not checker.add_spec(synthetic_spec, tool_types):
            raise RuntimeError("synthetic specification is unsatisfiable")
        if trace:
            trace_result = checker.set_trace(trace)
            if str(trace_result) != "sat":
                raise RuntimeError(f"synthetic trace is not satisfiable: {trace_result}")
        return checker.check(
            {"name": "delete", "arguments": {"resource_id": resource_id}}
        )

    diagnostics = io.StringIO()
    with contextlib.redirect_stdout(diagnostics):
        temporal_results = {
            "no_authorization_delete_A": check_with_trace([], "A"),
            "authorized_A_delete_A": check_with_trace(
                [
                    {
                        "name": "authorize",
                        "arguments": {"resource_id": "A"},
                        "output": "",
                    }
                ],
                "A",
            ),
            "authorized_A_delete_B": check_with_trace(
                [
                    {
                        "name": "authorize",
                        "arguments": {"resource_id": "A"},
                        "output": "",
                    }
                ],
                "B",
            ),
        }

    expected_temporal_results = {
        "no_authorization_delete_A": False,
        "authorized_A_delete_A": True,
        "authorized_A_delete_B": False,
    }
    report = {
        "schema_version": "sentinel.agent-c-checker-smoke.v1",
        "evidence_class": "artifact-replication-with-cpu-minimal-environment",
        "zenodo_record": "10.5281/zenodo.21095899",
        "archive": {
            "filename": archive.name,
            "size_bytes": archive.stat().st_size,
            "md5": archive_md5,
        },
        "requirements_sha256": _digest(
            artifact_root / "requirements.txt", "sha256"
        ),
        "minimal_environment": {
            package: version(package)
            for package in ("lark", "z3-solver", "nltk", "gensim", "numpy", "scipy")
        },
        "released_spec_counts": released_spec_counts,
        "released_specs_total": sum(released_spec_counts.values()),
        "empty_unconstrained_spec_counts": empty_spec_counts,
        "nonempty_specs_parsed": (
            sum(released_spec_counts.values()) - sum(empty_spec_counts.values())
        ),
        "released_spec_validation": "grammar-syntax-only",
        "parse_failures": parse_failures,
        "synthetic_temporal_spec": synthetic_spec,
        "temporal_results": temporal_results,
        "expected_temporal_results": expected_temporal_results,
        "temporal_results_match": temporal_results == expected_temporal_results,
        "captured_checker_diagnostics": diagnostics.getvalue().splitlines(),
        "substitutions_and_omissions": [
            "Installed only CPU-native model-free checker dependencies from the pinned requirements.",
            "Did not install unconditional CUDA/NVIDIA packages, triton, torch, transformers, or the nested constrained-generation packages.",
            "Released domain specs were grammar-parsed without the runtime tool-type dictionary; semantic checking is limited to the explicit synthetic rule.",
            "Did not instantiate an LLM, run a tau2 conversation, or reproduce a reported paper metric.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not parse_failures and report["temporal_results_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
