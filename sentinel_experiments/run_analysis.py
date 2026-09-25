"""Integrity checks and explicitly descriptive analysis for terminal records."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from scipy.stats import beta

from .contracts import digest


def clopper_pearson(events: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    if trials <= 0 or not 0 <= events <= trials:
        raise ValueError("events and trials must satisfy 0 <= events <= trials")
    lower = 0.0 if events == 0 else float(beta.ppf(alpha / 2, events, trials - events + 1))
    upper = (
        1.0
        if events == trials
        else float(beta.ppf(1 - alpha / 2, events + 1, trials - events))
    )
    return lower, upper


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify_run(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = _load_json(run_dir / "manifest.json")
    expected_manifest_digest = manifest.pop("manifest_digest")
    if digest(manifest) != expected_manifest_digest:
        raise ValueError("manifest digest mismatch")
    manifest["manifest_digest"] = expected_manifest_digest

    records = [
        json.loads(line)
        for line in (run_dir / "results.jsonl").read_text().splitlines()
        if line
    ]
    identifiers: set[str] = set()
    for record in records:
        expected_record_digest = record.pop("record_digest")
        if digest(record) != expected_record_digest:
            raise ValueError(f"record digest mismatch: {record['trial_id']}")
        record["record_digest"] = expected_record_digest
        if record["trial_id"] in identifiers:
            raise ValueError(f"duplicate trial id: {record['trial_id']}")
        identifiers.add(record["trial_id"])

    specs = {spec["trial_id"]: spec for spec in manifest["specs"]}
    if identifiers != set(specs):
        raise ValueError("manifest/result trial IDs differ")
    for record in records:
        if record["spec_digest"] != digest(specs[record["trial_id"]]):
            raise ValueError(f"spec digest mismatch: {record['trial_id']}")
    return manifest, records


def _event(record: dict[str, Any], outcome: str) -> bool:
    oracle = record["oracle"]
    if outcome == "safe_recovery":
        return bool(oracle["safe"] and oracle["recovered"])
    if outcome == "observation_disagreement":
        return bool(oracle["claimed_recovered"] != oracle["recovered"])
    return bool(oracle[outcome])


def _rates(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(records)
    result: dict[str, Any] = {"trials": len(items)}
    for outcome in (
        "unauthorized_effect",
        "safe_recovery",
        "observation_disagreement",
    ):
        events = sum(_event(record, outcome) for record in items)
        lower, upper = clopper_pearson(events, len(items))
        result[outcome] = {
            "events": events,
            "proportion": events / len(items),
            "clopper_pearson_95": [lower, upper],
        }
    return result


def _paired_contrast(
    records: Iterable[dict[str, Any]],
    left: str,
    right: str,
    outcome: str,
    include: Callable[[dict[str, Any]], bool] = lambda record: True,
) -> dict[str, Any]:
    indexed: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        system, _, design_row = record["trial_id"].split("--")
        if include(record):
            indexed[(system, design_row)][record["guardrail"]] = record
    pairs = [value for value in indexed.values() if left in value and right in value]
    left_events = sum(_event(pair[left], outcome) for pair in pairs)
    right_events = sum(_event(pair[right], outcome) for pair in pairs)
    return {
        "left": left,
        "right": right,
        "outcome": outcome,
        "paired_rows": len(pairs),
        "left_events": left_events,
        "right_events": right_events,
        "risk_difference": (left_events - right_events) / len(pairs) if pairs else None,
        "left_only": sum(
            _event(pair[left], outcome) and not _event(pair[right], outcome)
            for pair in pairs
        ),
        "right_only": sum(
            _event(pair[right], outcome) and not _event(pair[left], outcome)
            for pair in pairs
        ),
    }


def analyze_run(run_dir: Path, *, confirmatory: bool = False) -> dict[str, Any]:
    manifest, records = verify_run(run_dir)
    simulated = any("/simulated/" in record["incident_id"] for record in records)
    if confirmatory and simulated:
        raise ValueError("simulator records are ineligible for confirmatory analysis")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["guardrail"]].append(record)
    report = {
        "schema_version": "sentinel.preflight-analysis.v1",
        "run_manifest_digest": manifest["manifest_digest"],
        "evidence_class": "simulator_preflight" if simulated else "live_candidate",
        "confirmatory_eligible": not simulated,
        "integrity": {
            "records": len(records),
            "unique_trial_ids": len({record["trial_id"] for record in records}),
            "manifest_and_record_digests_verified": True,
        },
        "descriptive_by_guardrail": {
            guardrail: _rates(items) for guardrail, items in sorted(grouped.items())
        },
        "preflight_contrasts": {
            "C1": _paired_contrast(
                records,
                "guardian",
                "schema_allowlist",
                "unauthorized_effect",
                lambda record: "predictor.wrong_service" in record["faults"],
            ),
            "C2": _paired_contrast(
                records,
                "guardian",
                "external_policy",
                "unauthorized_effect",
                lambda record: any(
                    fault.startswith("binding.") for fault in record["faults"]
                ),
            ),
            "C5": _paired_contrast(
                records, "guardian", "always_deny", "safe_recovery"
            ),
        },
        "limitations": [
            "Rows are deliberately selected fault configurations, not a random sample.",
            "Both system labels use the same deterministic microservice simulator.",
            "Intervals describe selected rows and are not field-risk confidence intervals.",
            "No repeated live trials or environment-level variance are present.",
        ],
    }
    report["report_digest"] = digest(report)
    return report
