"""Append-only, baseline-neutral action/effect evidence records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .contracts import _json_value, digest


class EventStatus(str, Enum):
    OBSERVED = "observed"
    NOT_OBSERVED = "not_observed"
    NOT_APPLICABLE = "not_applicable"


class TraceStage(str, Enum):
    PROPOSAL = "proposal"
    NORMALIZED_ACTION = "normalized_action"
    TRUSTED_BINDING = "trusted_binding"
    NATIVE_VERDICT = "native_verdict"
    DISPATCH = "dispatch"
    RECEIPT = "receipt"
    EFFECT = "effect"
    STATE = "state"


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    event_id: str
    stage: TraceStage
    status: EventStatus
    source_namespace: str
    semantics: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    previous_event_digest: str | None = None
    event_digest: str = ""

    @classmethod
    def create(
        cls,
        *,
        sequence: int,
        event_id: str,
        stage: TraceStage,
        status: EventStatus,
        source_namespace: str,
        semantics: str,
        payload: Mapping[str, Any] | None = None,
        previous_event_digest: str | None = None,
    ) -> TraceEvent:
        event_payload = _json_value(dict(payload or {}))
        if status is not EventStatus.OBSERVED and event_payload:
            raise ValueError("unobserved or inapplicable events cannot carry payload")
        material = {
            "sequence": sequence,
            "event_id": event_id,
            "stage": stage.value,
            "status": status.value,
            "source_namespace": source_namespace,
            "semantics": semantics,
            "payload": event_payload,
            "previous_event_digest": previous_event_digest,
        }
        return cls(
            sequence=sequence,
            event_id=event_id,
            stage=stage,
            status=status,
            source_namespace=source_namespace,
            semantics=semantics,
            payload=event_payload,
            previous_event_digest=previous_event_digest,
            event_digest=digest(material),
        )

    def material(self) -> dict[str, Any]:
        value = _json_value(asdict(self))
        value.pop("event_digest")
        return value


@dataclass(frozen=True)
class ActionEffectTrace:
    trace_id: str
    baseline: str
    evidence_class: str
    source_report_sha256: str
    native_namespace: Mapping[str, Any]
    faults: tuple[str, ...] = ()
    events: tuple[TraceEvent, ...] = ()
    schema_version: str = "sentinel.action-effect-trace.v1"

    def validate(self) -> None:
        previous: str | None = None
        event_ids: set[str] = set()
        for expected_sequence, event in enumerate(self.events, start=1):
            if event.sequence != expected_sequence:
                raise ValueError("event sequences must be contiguous and start at one")
            if event.event_id in event_ids:
                raise ValueError(f"duplicate event_id: {event.event_id}")
            if event.previous_event_digest != previous:
                raise ValueError("event digest chain is broken")
            if event.event_digest != digest(event.material()):
                raise ValueError("event digest does not match event material")
            if event.status is not EventStatus.OBSERVED and event.payload:
                raise ValueError("unobserved or inapplicable event carries payload")
            event_ids.add(event.event_id)
            previous = event.event_digest

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        value = _json_value(asdict(self))
        value["native_namespace_digest"] = digest(value["native_namespace"])
        value["record_digest"] = digest(value)
        return value


class TraceBuilder:
    """Build a new immutable hash chain; existing events are never modified."""

    def __init__(
        self,
        *,
        trace_id: str,
        baseline: str,
        evidence_class: str,
        source_report_sha256: str,
        native_namespace: Mapping[str, Any],
        faults: Sequence[str] = (),
    ):
        self._header = {
            "trace_id": trace_id,
            "baseline": baseline,
            "evidence_class": evidence_class,
            "source_report_sha256": source_report_sha256,
            "native_namespace": _json_value(dict(native_namespace)),
            "faults": tuple(faults),
        }
        self._events: list[TraceEvent] = []

    def append(
        self,
        *,
        event_id: str,
        stage: TraceStage,
        status: EventStatus,
        source_namespace: str,
        semantics: str,
        payload: Mapping[str, Any] | None = None,
    ) -> TraceBuilder:
        previous = self._events[-1].event_digest if self._events else None
        self._events.append(
            TraceEvent.create(
                sequence=len(self._events) + 1,
                event_id=event_id,
                stage=stage,
                status=status,
                source_namespace=source_namespace,
                semantics=semantics,
                payload=payload,
                previous_event_digest=previous,
            )
        )
        return self

    def build(self) -> ActionEffectTrace:
        trace = ActionEffectTrace(events=tuple(self._events), **self._header)
        trace.validate()
        return trace


def compare_boolean_fields(
    trace: ActionEffectTrace,
    *,
    comparison_id: str,
    left_event_id: str,
    left_field: str,
    right_event_id: str,
    right_field: str,
) -> dict[str, Any]:
    """Compare two explicitly named booleans without redefining native metrics."""
    events = {event.event_id: event for event in trace.events}
    left = events.get(left_event_id)
    right = events.get(right_event_id)
    result = {
        "comparison_id": comparison_id,
        "relation": "boolean_equality",
        "left": {"event_id": left_event_id, "field": left_field},
        "right": {"event_id": right_event_id, "field": right_field},
        "status": "not_computable",
        "left_value": None,
        "right_value": None,
    }
    if (
        left is None
        or right is None
        or left.status is not EventStatus.OBSERVED
        or right.status is not EventStatus.OBSERVED
    ):
        return result
    left_value = left.payload.get(left_field)
    right_value = right.payload.get(right_field)
    if not isinstance(left_value, bool) or not isinstance(right_value, bool):
        return result
    result.update(
        {
            "status": "agree" if left_value == right_value else "disagree",
            "left_value": left_value,
            "right_value": right_value,
        }
    )
    return result
