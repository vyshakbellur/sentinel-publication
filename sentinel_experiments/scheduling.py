"""Deterministic blocked scheduling for the blinded live pilot."""

from __future__ import annotations

import hashlib
import hmac
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .contracts import digest
from .study_execution import (
    SUPPORTED_LIVE_FAULTS,
    StudyAssignment,
    bind_study_assignment,
)


class PilotOutcome(Protocol):
    @property
    def succeeded(self) -> bool: ...


@dataclass(frozen=True)
class ScheduleExecution:
    attempted_trial_ids: tuple[str, ...]
    completed: bool
    stopped_at_trial_id: str | None


def _randomization_key(
    seed: str,
    block_id: str,
    system: str,
    guardrail: str,
    row_id: str,
) -> str:
    return digest(
        {
            "seed": seed,
            "block_id": block_id,
            "system": system,
            "guardrail": guardrail,
            "design_row_id": row_id,
        }
    )


def generate_pilot_schedule(
    protocol: dict[str, Any],
    design: dict[str, Any],
    partition: dict[str, Any],
    block_contract: dict[str, Any],
) -> dict[str, Any]:
    """Generate complete, reproducibly randomized blocks without executing them."""
    systems = tuple(protocol["systems"])
    guardrails = tuple(protocol["guardrails"])
    row_ids = tuple(partition["pilot"]["row_ids"])
    known_rows = {row["row_id"] for row in design["rows"]}
    if not set(row_ids) <= known_rows:
        raise ValueError("pilot schedule references unknown design rows")
    blocks = block_contract["blocks"]
    minimum = partition["pilot"]["minimum_independent_deployment_blocks_per_system"]
    if len(blocks) < minimum:
        raise ValueError("pilot schedule has too few independent blocks")
    block_ids = [block["block_id"] for block in blocks]
    if len(block_ids) != len(set(block_ids)):
        raise ValueError("pilot block IDs must be unique")

    rows: list[dict[str, Any]] = []
    seed = block_contract["randomization_seed"]
    for block in blocks:
        block_id = block["block_id"]
        mappings = (
            block["deployment_instance_ids"],
            block["incident_template_ids"],
            block["load_seeds"],
        )
        if any(set(mapping) != set(systems) for mapping in mappings):
            raise ValueError("every block mapping must cover exactly the frozen systems")
        for system in systems:
            cells = [
                {
                    "guardrail": guardrail,
                    "design_row_id": row_id,
                    "randomization_key": _randomization_key(
                        seed, block_id, system, guardrail, row_id
                    ),
                }
                for guardrail in guardrails
                for row_id in row_ids
            ]
            cells.sort(key=lambda item: item["randomization_key"])
            for position, cell in enumerate(cells, start=1):
                trial_id = f"PILOT-{block_id}-{system}-{position:03d}"
                rows.append(
                    {
                        "schedule_index": len(rows) + 1,
                        "trial_id": trial_id,
                        "block_id": block_id,
                        "system": system,
                        **cell,
                        "assignment": {
                            "phase": "pilot",
                            "design_row_id": cell["design_row_id"],
                            "deployment_instance_id": block[
                                "deployment_instance_ids"
                            ][system],
                            "incident_template_id": block[
                                "incident_template_ids"
                            ][system],
                            "load_seed": block["load_seeds"][system],
                        },
                    }
                )
    schedule: dict[str, Any] = {
        "schema_version": "sentinel.pilot-schedule.v1",
        "mode": block_contract["mode"],
        "protocol_version": protocol["protocol_version"],
        "design_digest": design["design_digest"],
        "partition_digest": digest(partition),
        "randomization_seed": seed,
        "rows": rows,
    }
    schedule["schedule_digest"] = digest(schedule)
    return schedule


def audit_pilot_schedule(
    schedule: dict[str, Any],
    protocol: dict[str, Any],
    design: dict[str, Any],
    partition: dict[str, Any],
) -> dict[str, Any]:
    unsigned = dict(schedule)
    schedule_digest = unsigned.pop("schedule_digest", None)
    if not isinstance(schedule_digest, str) or digest(unsigned) != schedule_digest:
        raise ValueError("pilot schedule digest mismatch")
    if schedule.get("design_digest") != design.get("design_digest"):
        raise ValueError("pilot schedule design digest mismatch")
    if schedule.get("partition_digest") != digest(partition):
        raise ValueError("pilot schedule partition digest mismatch")
    rows = schedule["rows"]
    systems = tuple(protocol["systems"])
    guardrails = tuple(protocol["guardrails"])
    design_rows = tuple(partition["pilot"]["row_ids"])
    block_ids = sorted({row["block_id"] for row in rows})
    expected_cells = len(block_ids) * len(systems) * len(guardrails) * len(design_rows)
    if len(rows) != expected_cells:
        raise ValueError("pilot schedule is incomplete")
    trial_ids = [row["trial_id"] for row in rows]
    if len(trial_ids) != len(set(trial_ids)):
        raise ValueError("pilot schedule contains duplicate trial IDs")
    cells = Counter(
        (row["block_id"], row["system"], row["guardrail"], row["design_row_id"])
        for row in rows
    )
    expected = {
        (block_id, system, guardrail, row_id)
        for block_id in block_ids
        for system in systems
        for guardrail in guardrails
        for row_id in design_rows
    }
    if set(cells) != expected or set(cells.values()) != {1}:
        raise ValueError("pilot schedule cells are not unique and complete")
    per_system_block = Counter((row["block_id"], row["system"]) for row in rows)
    if set(per_system_block.values()) != {len(guardrails) * len(design_rows)}:
        raise ValueError("pilot block allocation is unbalanced")
    if any(row["assignment"]["phase"] != "pilot" for row in rows):
        raise ValueError("pilot schedule contains a non-pilot assignment")
    if [row["schedule_index"] for row in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("pilot schedule indices are not contiguous")
    for row in rows:
        expected_key = _randomization_key(
            schedule["randomization_seed"],
            row["block_id"],
            row["system"],
            row["guardrail"],
            row["design_row_id"],
        )
        if row["randomization_key"] != expected_key:
            raise ValueError("pilot randomization key mismatch")
        assignment = StudyAssignment(**row["assignment"])
        binding = bind_study_assignment(
            row["trial_id"],
            assignment,
            protocol,
            design,
            partition,
            SUPPORTED_LIVE_FAULTS,
        )
        if binding.phase != "pilot" or binding.confirmatory_eligible:
            raise ValueError("pilot schedule row has an invalid study binding")

    report: dict[str, Any] = {
        "schema_version": "sentinel.pilot-schedule-audit.v1",
        "schedule_digest": schedule_digest,
        "mode": schedule["mode"],
        "blocks": len(block_ids),
        "system_blocks": len(per_system_block),
        "rows": len(rows),
        "unique_trial_ids": len(set(trial_ids)),
        "unique_cells": len(cells),
        "rows_per_system_block": sorted(set(per_system_block.values())),
        "repetitions_per_system_guardrail_row": len(block_ids),
        "phase": "pilot",
        "confirmatory_eligible": False,
        "limitations": [
            "This is a contract-preflight schedule and does not represent execution.",
            "Placeholder deployment identifiers do not name Kubernetes resources.",
            "Randomization order does not provide outcomes, variance, or power.",
        ],
    }
    report["audit_digest"] = digest(report)
    return report


def blind_pilot_schedule(
    schedule: dict[str, Any], blinding_key: bytes
) -> dict[str, Any]:
    if not blinding_key:
        raise ValueError("blinding key must be non-empty")
    blinded_rows: list[dict[str, Any]] = []
    for row in schedule["rows"]:
        token = hmac.new(
            blinding_key,
            f"{row['trial_id']}:{row['guardrail']}".encode(),
            hashlib.sha256,
        ).hexdigest()
        blinded_rows.append(
            {
                "schedule_index": row["schedule_index"],
                "trial_id": row["trial_id"],
                "block_id": row["block_id"],
                "system": row["system"],
                "design_row_id": row["design_row_id"],
                "condition_token": token,
            }
        )
    blinded: dict[str, Any] = {
        "schema_version": "sentinel.blinded-pilot-schedule.v1",
        "source_schedule_digest": schedule["schedule_digest"],
        "blinding_key_digest": hashlib.sha256(blinding_key).hexdigest(),
        "rows": blinded_rows,
    }
    blinded["blinded_digest"] = digest(blinded)
    return blinded


def execute_schedule(
    schedule: dict[str, Any],
    run_cell: Callable[[dict[str, Any]], PilotOutcome],
) -> ScheduleExecution:
    """Execute in frozen order and stop after any unsuccessful terminal record."""
    attempted: list[str] = []
    for row in schedule["rows"]:
        result = run_cell(row)
        attempted.append(row["trial_id"])
        if not result.succeeded:
            return ScheduleExecution(tuple(attempted), False, row["trial_id"])
    return ScheduleExecution(tuple(attempted), True, None)
