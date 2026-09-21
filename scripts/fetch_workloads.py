"""Fetch the exact public workload revisions declared in the lock file."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "external" / "workloads.lock.json"


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def fetch(destination: Path, url: str, revision: str) -> None:
    if not destination.exists():
        run("git", "clone", "--filter=blob:none", "--no-checkout", url, str(destination))
    run("git", "fetch", "--depth=1", "origin", revision, cwd=destination)
    run("git", "checkout", "--detach", revision, cwd=destination)
    actual = subprocess.check_output(
        ("git", "rev-parse", "HEAD"), cwd=destination, text=True
    ).strip()
    if actual != revision:
        raise RuntimeError(f"revision mismatch for {destination.name}: {actual}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="*", help="workload IDs; default is all")
    parser.add_argument("--directory", type=Path, default=ROOT / "_workloads")
    args = parser.parse_args()
    data = json.loads(LOCK.read_text())
    selected = set(args.ids)
    known = {item["id"] for item in data["workloads"]}
    unknown = selected - known
    if unknown:
        parser.error(f"unknown workload IDs: {', '.join(sorted(unknown))}")
    args.directory.mkdir(parents=True, exist_ok=True)
    for item in data["workloads"]:
        if selected and item["id"] not in selected:
            continue
        fetch(args.directory / item["id"], item["url"], item["revision"])


if __name__ == "__main__":
    main()
