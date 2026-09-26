"""Reproduce all non-live artifact checks in a fresh virtual environment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "requirements/repro.lock"
TOOLS_LOCK = ROOT / "external/tools.lock.json"
PASS_COUNT = re.compile(r"(\d+) passed")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(excluded: Path | None) -> str:
    process = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = sorted(ROOT / item for item in process.stdout.splitlines())
    accumulator = hashlib.sha256()
    for path in paths:
        if not path.is_file() or (excluded is not None and path == excluded):
            continue
        relative = path.relative_to(ROOT).as_posix().encode()
        accumulator.update(len(relative).to_bytes(8, "big"))
        accumulator.update(relative)
        payload = path.read_bytes()
        accumulator.update(len(payload).to_bytes(8, "big"))
        accumulator.update(payload)
    return accumulator.hexdigest()


def run(arguments: list[str], *, environment: dict[str, str] | None = None) -> dict:
    started = time.monotonic()
    process = subprocess.run(
        arguments,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
        timeout=300,
    )
    output = (process.stdout + process.stderr).strip()
    result = {
        "command": arguments,
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": process.returncode,
        "output_tail": output[-4000:],
    }
    if process.returncode != 0:
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default="python3.12")
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    report_path = arguments.report.resolve()
    commands: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="sentinel-reproduce-") as directory:
        environment_dir = Path(directory) / "venv"
        commands.append(run([arguments.python, "-m", "venv", str(environment_dir)]))
        python = str(environment_dir / "bin/python")
        commands.append(
            run(
                [
                    python,
                    "-m",
                    "pip",
                    "install",
                    "--constraint",
                    str(LOCK),
                    "-e",
                    f"{ROOT}[dev,analysis]",
                ]
            )
        )
        commands.append(run([python, "scripts/fetch_tools.py"]))
        environment = dict(os.environ)
        environment["SENTINEL_OPA_BIN"] = str(ROOT / "_tools/opa")
        test_result = run([python, "-m", "pytest"], environment=environment)
        commands.append(test_result)
        commands.append(
            run(
                [
                    python,
                    "-m",
                    "ruff",
                    "check",
                    "sentinel_experiments",
                    "tests",
                    "scripts",
                ]
            )
        )
        commands.append(run([python, "-m", "scripts.check_references"]))
        version = run([python, "--version"])
        commands.append(version)

    match = PASS_COUNT.search(test_result["output_tail"])
    report = {
        "schema_version": "sentinel.reproduction-report.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": "non-live artifact verification; no Kubernetes system evidence",
        "platform": platform.platform(),
        "python": version["output_tail"],
        "dependency_lock_sha256": sha256(LOCK),
        "tools_lock_sha256": sha256(TOOLS_LOCK),
        "source_tree_sha256": source_digest(report_path),
        "test_count": None if match is None else int(match.group(1)),
        "commands": commands,
        "limitations": [
            "Dependency and OPA downloads require network access unless cached.",
            "This run does not provision or contact Kubernetes.",
            "The report is host-specific and is not a container-image attestation.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"wrote successful reproduction report to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
