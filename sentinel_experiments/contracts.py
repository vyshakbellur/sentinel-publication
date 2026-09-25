"""Stable experiment contracts and canonical record hashing."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class FaultLayer(str, Enum):
    EVIDENCE = "evidence"
    PREDICTOR = "predictor"
    BINDING = "binding"
    POLICY = "policy"
    ENFORCEMENT = "enforcement"
    OBSERVATION = "observation"


@dataclass(frozen=True)
class Fault:
    name: str
    layer: FaultLayer
    parameters: Mapping[str, Any] = field(default_factory=dict)

    @property
    def fault_id(self) -> str:
        return f"{self.layer.value}.{self.name}"


@dataclass(frozen=True)
class TrialSpec:
    trial_id: str
    incident_id: str
    expected_service: str
    guardrail: str = "guardian"
    proposal_service: str | None = None
    desired_replicas: int = 2
    faults: tuple[Fault, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return _json_value(asdict(self))

    @property
    def spec_digest(self) -> str:
        return digest(self.to_dict())


@dataclass(frozen=True)
class Decision:
    verdict: str
    allowed: bool
    reason_codes: tuple[str, ...] = ()
    canonical_service: str | None = None
    evidence_digest: str | None = None


@dataclass(frozen=True)
class Effect:
    effect_id: str
    operation: str
    service: str
    replicas: int
    sequence: int
    completed: bool = True
    compensates_effect_id: str | None = None


@dataclass(frozen=True)
class RecoveryObservation:
    elapsed_ms: int
    replicas: Mapping[str, int]
    fresh: bool = True


@dataclass(frozen=True)
class OracleResult:
    safe: bool
    recovered: bool
    unauthorized_effect: bool
    duplicate_effect: bool
    claimed_recovered: bool
    partial_effect: bool = False
    rollback_confirmed: bool = False
    delayed_regression: bool = False
    stale_observation: bool = False
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class TrialRecord:
    schema_version: str
    trial_id: str
    incident_id: str
    spec_digest: str
    guardrail: str
    faults: tuple[str, ...]
    evidence: Mapping[str, Any]
    proposal: Mapping[str, Any]
    decision: Decision
    effects: tuple[Effect, ...]
    final_state: Mapping[str, int]
    oracle: OracleResult

    def to_dict(self) -> dict[str, Any]:
        value = _json_value(asdict(self))
        value["record_digest"] = digest(value)
        return value


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        _json_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()
