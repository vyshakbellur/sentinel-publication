"""Fetch checksum-pinned external experiment tools."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "external" / "tools.lock.json"


def main() -> None:
    lock = json.loads(LOCK.read_text())
    key = f"{platform.system()}-{platform.machine()}"
    artifact = lock["tools"]["opa"]["artifacts"].get(key)
    if artifact is None:
        raise SystemExit(f"no locked OPA artifact for {key}")
    destination = ROOT / "_tools" / "opa"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(artifact["url"]) as response:
        payload = response.read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != artifact["sha256"]:
        raise RuntimeError(f"OPA checksum mismatch: {actual}")
    destination.write_bytes(payload)
    os.chmod(destination, 0o755)
    print(f"installed OPA {lock['tools']['opa']['version']} at {destination}")


if __name__ == "__main__":
    main()
