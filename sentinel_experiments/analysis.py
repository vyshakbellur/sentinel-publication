"""Counterexample minimization for SENTINEL assurance outcomes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from itertools import combinations

from .contracts import TrialRecord, TrialSpec
from .harness import run_trial

OutcomePredicate = Callable[[TrialRecord], bool]


def minimal_fault_sets(
    spec: TrialSpec,
    predicate: OutcomePredicate,
) -> tuple[tuple[str, ...], ...]:
    """Return all smallest fault subsets that preserve an observed outcome."""
    faults = tuple(spec.faults)
    if not predicate(run_trial(spec)):
        return ()
    for size in range(len(faults) + 1):
        matches: list[tuple[str, ...]] = []
        for subset in combinations(faults, size):
            candidate = replace(spec, faults=tuple(subset))
            if predicate(run_trial(candidate)):
                matches.append(tuple(sorted(fault.fault_id for fault in subset)))
        if matches:
            return tuple(sorted(set(matches)))
    return ()


def analyze_cut_sets(specs: tuple[TrialSpec, ...]) -> dict[str, object]:
    outcomes: tuple[tuple[str, OutcomePredicate], ...] = (
        (
            "unauthorized_effect",
            lambda record: record.oracle.unauthorized_effect,
        ),
        (
            "observation_disagreement",
            lambda record: record.oracle.claimed_recovered
            != record.oracle.recovered,
        ),
    )
    findings: list[dict[str, object]] = []
    for spec in specs:
        for outcome, predicate in outcomes:
            cut_sets = minimal_fault_sets(spec, predicate)
            if not cut_sets:
                continue
            findings.append(
                {
                    "trial_id": spec.trial_id,
                    "guardrail": spec.guardrail,
                    "outcome": outcome,
                    "minimum_size": len(cut_sets[0]),
                    "minimal_fault_sets": [list(item) for item in cut_sets],
                }
            )
    return {
        "schema_version": "sentinel.cut_sets.v1",
        "findings": findings,
    }
