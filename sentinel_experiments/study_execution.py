"""Fail-closed binding of live trials to the frozen study partition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import digest

SUPPORTED_LIVE_FAULTS = frozenset(
    {
        "evidence.stale_service",
        "predictor.wrong_service",
        "binding.cross_tenant",
        "binding.forged_authority",
        "binding.stale_manifest",
        "policy.overbroad_scope",
        "observation.false_success",
        "enforcement.argument_substitution",
        "enforcement.bypass",
        "enforcement.drop_effect",
        "enforcement.duplicate_retry",
    }
)


@dataclass(frozen=True)
class StudyAssignment:
    phase: str
    design_row_id: str
    deployment_instance_id: str
    incident_template_id: str
    load_seed: str


@dataclass(frozen=True)
class StudyBinding:
    phase: str
    design_row_id: str
    faults: tuple[str, ...]
    partition_version: str
    partition_digest: str
    design_digest: str
    independent_block_id: str
    confirmatory_eligible: bool


def bind_study_assignment(
    trial_id: str,
    assignment: StudyAssignment,
    protocol: dict[str, Any],
    design: dict[str, Any],
    partition: dict[str, Any],
    supported_faults: frozenset[str] = frozenset(),
) -> StudyBinding:
    """Validate phase, row, provenance, and inference eligibility."""
    if partition.get("status") != "frozen-before-live-pilot-outcomes":
        raise ValueError("study partition is not frozen")
    if partition.get("amends_protocol_version") != protocol.get("protocol_version"):
        raise ValueError("study partition/protocol version mismatch")
    if partition.get("design_digest") != design.get("design_digest"):
        raise ValueError("study partition/design digest mismatch")

    prefixes = partition["data_separation"]["run_id_prefixes"]
    if assignment.phase not in prefixes:
        raise ValueError("unknown study phase")
    if not trial_id.startswith(prefixes[assignment.phase]):
        raise ValueError("trial ID does not carry the required phase prefix")

    rows = {row["row_id"]: row for row in design["rows"]}
    if assignment.design_row_id not in rows:
        raise ValueError("unknown frozen design row")
    row = rows[assignment.design_row_id]
    if assignment.phase == "pilot":
        allowed_rows = set(partition["pilot"]["row_ids"])
        eligible = bool(partition["pilot"]["eligible_for_primary_inference"])
    elif assignment.phase == "confirmatory":
        allowed_rows = set(partition["confirmatory_subset"]["row_ids"])
        eligible = bool(
            partition["confirmatory_subset"]["eligible_for_primary_inference"]
        )
        if not isinstance(partition["confirmatory_subset"]["repetitions"], int):
            raise ValueError(
                "confirmatory phase is locked until pilot-based repetitions freeze"
            )
    else:
        allowed_rows = set(rows)
        eligible = bool(
            partition["fault_surface_census"]["eligible_for_primary_inference"]
        )
    if assignment.design_row_id not in allowed_rows:
        raise ValueError("design row is not allocated to this study phase")
    unsupported = set(row["faults"]) - supported_faults
    if unsupported:
        raise ValueError(
            "live fault adapter is not implemented for: "
            + ", ".join(sorted(unsupported))
        )

    block_fields = (
        assignment.deployment_instance_id,
        assignment.incident_template_id,
        assignment.load_seed,
    )
    if any(not value.strip() for value in block_fields):
        raise ValueError("independent-block fields must be non-empty")
    block = {
        "deployment_instance_id": assignment.deployment_instance_id,
        "incident_template_id": assignment.incident_template_id,
        "load_seed": assignment.load_seed,
    }
    return StudyBinding(
        phase=assignment.phase,
        design_row_id=assignment.design_row_id,
        faults=tuple(row["faults"]),
        partition_version=partition["partition_version"],
        partition_digest=digest(partition),
        design_digest=design["design_digest"],
        independent_block_id=digest(block),
        confirmatory_eligible=eligible,
    )


def require_confirmatory_records(
    records: list[dict[str, Any]],
    protocol: dict[str, Any],
    design: dict[str, Any],
    partition: dict[str, Any],
) -> None:
    """Fail closed if non-confirmatory evidence reaches primary analysis."""
    if not records:
        raise ValueError("confirmatory analysis requires records")
    for record in records:
        payload = dict(record)
        record_digest = payload.pop("record_digest", None)
        if not isinstance(record_digest, str) or digest(payload) != record_digest:
            raise ValueError("confirmatory record digest mismatch")
        study = record.get("study")
        if not isinstance(study, dict):
            raise TypeError("record lacks a study binding")
        if study.get("phase") != "confirmatory":
            raise ValueError("non-confirmatory record reached primary analysis")
        if study.get("confirmatory_eligible") is not True:
            raise ValueError("record is not marked confirmatory-eligible")
        if record.get("protocol_digest") != digest(protocol):
            raise ValueError("record protocol digest mismatch")
        if study.get("partition_digest") != digest(partition):
            raise ValueError("record partition digest mismatch")
        if study.get("design_digest") != design.get("design_digest"):
            raise ValueError("record design digest mismatch")
