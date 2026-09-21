"""Immutable run writing and initial effect-grounded summaries."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from collections.abc import Iterable
from pathlib import Path

from .analysis import analyze_cut_sets
from .contracts import TrialRecord, TrialSpec, canonical_json, digest


def _source_inventory() -> dict[str, str]:
    package_root = Path(__file__).parent
    return {
        path.relative_to(package_root.parent).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(package_root.glob("*.py"))
    }


def _git_state(repo: str | None) -> dict[str, object]:
    if not repo:
        return {"path": "unrecorded", "revision": None, "dirty": None}
    path = Path(repo).resolve()
    try:
        revision = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {"path": str(path), "revision": None, "dirty": None}
    return {"path": str(path), "revision": revision, "dirty": bool(status.strip())}


def summarize(records: Iterable[TrialRecord]) -> dict[str, object]:
    items = list(records)
    total = len(items)
    unsafe = sum(record.oracle.unauthorized_effect for record in items)
    recovered = sum(record.oracle.recovered for record in items)
    safe_recovered = sum(
        record.oracle.safe and record.oracle.recovered for record in items
    )
    disagreements = sum(
        record.oracle.claimed_recovered != record.oracle.recovered
        for record in items
    )
    return {
        "schema_version": "sentinel.summary.v1",
        "trials": total,
        "unauthorized_effects": unsafe,
        "unauthorized_effect_rate": unsafe / total if total else 0.0,
        "recovered": recovered,
        "safe_recoveries": safe_recovered,
        "safe_recovery_rate": safe_recovered / total if total else 0.0,
        "observation_disagreements": disagreements,
    }


def write_run(
    output: Path,
    specs: Iterable[TrialSpec],
    records: Iterable[TrialRecord],
) -> None:
    specs = list(specs)
    records = list(records)
    if output.exists():
        raise FileExistsError(
            f"refusing to overwrite existing experiment directory: {output}"
        )
    manifest = {
        "schema_version": "sentinel.manifest.v2",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "sentinel_sources": _source_inventory(),
        "guardian": _git_state(os.environ.get("GUARDIAN_REPO")),
        "specs": [spec.to_dict() for spec in specs],
    }
    manifest["manifest_digest"] = digest(manifest)
    output.mkdir(parents=True)
    (output / "manifest.json").write_bytes(canonical_json(manifest) + b"\n")
    with (output / "results.jsonl").open("xb") as stream:
        for record in records:
            stream.write(canonical_json(record.to_dict()) + b"\n")
    (output / "summary.json").write_text(
        json.dumps(summarize(records), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "cut_sets.json").write_text(
        json.dumps(analyze_cut_sets(tuple(specs)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
