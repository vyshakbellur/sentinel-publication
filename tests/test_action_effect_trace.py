import pytest

from sentinel_experiments.action_effect_trace import (
    ActionEffectTrace,
    EventStatus,
    TraceBuilder,
    TraceEvent,
    TraceStage,
    compare_boolean_fields,
    compare_event_fields,
)


def _trace():
    return (
        TraceBuilder(
            trace_id="trace-1",
            baseline="fixture",
            evidence_class="test",
            source_report_sha256="a" * 64,
            native_namespace={"metric": True},
        )
        .append(
            event_id="verdict",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="fixture verdict",
            payload={"positive": True},
        )
        .append(
            event_id="effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED,
            source_namespace="independent",
            semantics="fixture effect",
            payload={"completed": False},
        )
        .build()
    )


def test_trace_is_hash_chained_and_native_namespace_is_preserved():
    trace = _trace()
    payload = trace.to_dict()
    assert payload["native_namespace"] == {"metric": True}
    assert payload["events"][1]["previous_event_digest"] == payload["events"][0][
        "event_digest"
    ]
    assert payload["record_digest"]


def test_explicit_boolean_comparison_detects_disagreement():
    comparison = compare_boolean_fields(
        _trace(),
        comparison_id="verdict_effect",
        left_event_id="verdict",
        left_field="positive",
        right_event_id="effect",
        right_field="completed",
    )
    assert comparison["status"] == "disagree"
    assert comparison["left_value"] is True
    assert comparison["right_value"] is False


def test_missing_observation_is_not_silently_treated_as_false():
    trace = (
        TraceBuilder(
            trace_id="trace-missing",
            baseline="fixture",
            evidence_class="test",
            source_report_sha256="b" * 64,
            native_namespace={},
        )
        .append(
            event_id="verdict",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="fixture verdict",
            payload={"positive": True},
        )
        .append(
            event_id="effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.NOT_OBSERVED,
            source_namespace="independent",
            semantics="fixture has no effect oracle",
        )
        .build()
    )
    comparison = compare_boolean_fields(
        trace,
        comparison_id="verdict_effect",
        left_event_id="verdict",
        left_field="positive",
        right_event_id="effect",
        right_field="completed",
    )
    assert comparison["status"] == "not_computable"
    assert comparison["right_value"] is None


def test_exact_scalar_comparison_preserves_type_and_missingness():
    trace = (
        TraceBuilder(
            trace_id="trace-targets",
            baseline="fixture",
            evidence_class="test",
            source_report_sha256="c" * 64,
            native_namespace={},
        )
        .append(
            event_id="decision",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="authorized target",
            payload={"target": "adservice", "count": 1},
        )
        .append(
            event_id="effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED,
            source_namespace="independent",
            semantics="observed target",
            payload={"target": "cartservice", "count": 1},
        )
        .build()
    )
    target = compare_event_fields(
        trace,
        comparison_id="target",
        left_event_id="decision",
        left_field="target",
        right_event_id="effect",
        right_field="target",
    )
    count = compare_event_fields(
        trace,
        comparison_id="count",
        left_event_id="decision",
        left_field="count",
        right_event_id="effect",
        right_field="count",
        expected_type=int,
    )
    assert target["status"] == "disagree"
    assert count["status"] == "agree"


def test_scalar_comparison_does_not_treat_null_as_an_observation():
    trace = (
        TraceBuilder(
            trace_id="trace-null",
            baseline="fixture",
            evidence_class="test",
            source_report_sha256="d" * 64,
            native_namespace={},
        )
        .append(
            event_id="decision",
            stage=TraceStage.NATIVE_VERDICT,
            status=EventStatus.OBSERVED,
            source_namespace="native",
            semantics="authorized target",
            payload={"target": "adservice"},
        )
        .append(
            event_id="effect",
            stage=TraceStage.EFFECT,
            status=EventStatus.OBSERVED,
            source_namespace="independent",
            semantics="no target observed",
            payload={"target": None},
        )
        .build()
    )
    comparison = compare_event_fields(
        trace,
        comparison_id="target",
        left_event_id="decision",
        left_field="target",
        right_event_id="effect",
        right_field="target",
    )
    assert comparison["status"] == "not_computable"


def test_unobserved_event_rejects_payload():
    with pytest.raises(ValueError, match="cannot carry payload"):
        TraceEvent.create(
            sequence=1,
            event_id="bad",
            stage=TraceStage.EFFECT,
            status=EventStatus.NOT_OBSERVED,
            source_namespace="independent",
            semantics="bad fixture",
            payload={"completed": False},
        )


def test_tampered_chain_fails_validation():
    trace = _trace()
    bad_second = TraceEvent(
        **{
            **trace.events[1].__dict__,
            "previous_event_digest": "0" * 64,
        }
    )
    tampered = ActionEffectTrace(
        trace_id=trace.trace_id,
        baseline=trace.baseline,
        evidence_class=trace.evidence_class,
        source_report_sha256=trace.source_report_sha256,
        native_namespace=trace.native_namespace,
        events=(trace.events[0], bad_second),
    )
    with pytest.raises(ValueError, match="digest chain"):
        tampered.validate()
