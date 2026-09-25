"""Always-deny and external OPA policy baselines."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import Decision


class OpaUnavailable(RuntimeError):
    """Raised when the pinned OPA executable cannot be located."""


@dataclass(frozen=True)
class AlwaysDenySubject:
    def decide(self, proposal: Mapping[str, Any]) -> Decision:
        del proposal
        return Decision(
            verdict="BLOCK",
            allowed=False,
            reason_codes=("ALWAYS_DENY_BASELINE",),
        )


@dataclass(frozen=True)
class OpaPolicySubject:
    services: tuple[str, ...] = ("adservice", "cartservice")
    binary: str | None = None
    policy_path: Path = Path(__file__).parents[1] / "policies/opa/remediation.rego"

    def _binary(self) -> str:
        candidate = self.binary or os.environ.get("SENTINEL_OPA_BIN") or shutil.which(
            "opa"
        )
        if not candidate:
            raise OpaUnavailable(
                "OPA is unavailable; run scripts/fetch_tools.py and set "
                "SENTINEL_OPA_BIN=_tools/opa"
            )
        return candidate

    def decide(
        self,
        proposal: Mapping[str, Any],
        *,
        expected_service: str,
        faults: frozenset[str],
    ) -> Decision:
        allowed_scope = (
            list(self.services)
            if "policy.overbroad_scope" in faults
            else [expected_service]
        )
        policy_input = {
            "proposal": proposal,
            "trusted": {
                "allowed_services": list(self.services),
                "allowed_scope": allowed_scope,
            },
        }
        process = subprocess.run(
            [
                self._binary(),
                "eval",
                "--format=json",
                "--data",
                str(self.policy_path),
                "--stdin-input",
                "data.sentinel.allow",
            ],
            input=json.dumps(policy_input),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        output = json.loads(process.stdout)
        allowed = bool(output["result"][0]["expressions"][0]["value"])
        service = proposal.get("arguments", {}).get("service") if allowed else None
        return Decision(
            verdict="ALLOW" if allowed else "BLOCK",
            allowed=allowed,
            reason_codes=("OPA_POLICY_ALLOW" if allowed else "OPA_POLICY_DENY",),
            canonical_service=service,
        )
