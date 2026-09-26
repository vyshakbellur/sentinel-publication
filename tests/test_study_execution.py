import json
from copy import deepcopy
from pathlib import Path

import pytest

from sentinel_experiments.contracts import digest
from sentinel_experiments.study_execution import (
    StudyAssignment,
    bind_study_assignment,
    require_confirmatory_records,
)

ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments" / "protocol"


def inputs():
    protocol = json.loads((PROTOCOL / "confirmatory_protocol.json").read_text())
    design = json.loads((PROTOCOL / "pairwise_design.json").read_text())
    partition = json.loads((PROTOCOL / "study_partition.json").read_text())
    return protocol, design, partition


def assignment(phase="pilot", row="PW000"):
    return StudyAssignment(phase, row, "deploy-1", "replicas-zero", "seed-1")


def signed_record(phase, eligible, protocol, design, partition):
    record = {
        "protocol_digest": digest(protocol),
        "study": {
            "phase": phase,
            "confirmatory_eligible": eligible,
            "partition_digest": digest(partition),
            "design_digest": design["design_digest"],
        },
    }
    record["record_digest"] = digest(record)
    return record


def test_nominal_pilot_binding_is_non_confirmatory_and_digested():
    binding = bind_study_assignment("PILOT-001", assignment(), *inputs())
    assert binding.phase == "pilot"
    assert binding.design_row_id == "PW000"
    assert not binding.confirmatory_eligible
    assert len(binding.independent_block_id) == 64


def test_phase_prefix_and_fault_adapter_fail_closed():
    with pytest.raises(ValueError, match="phase prefix"):
        bind_study_assignment("CONF-001", assignment(), *inputs())
    with pytest.raises(ValueError, match="fault adapter"):
        bind_study_assignment("PILOT-002", assignment(row="PW001"), *inputs())


def test_confirmatory_execution_is_locked_until_repetitions_freeze():
    with pytest.raises(ValueError, match="repetitions freeze"):
        bind_study_assignment(
            "CONF-001", assignment("confirmatory", "PW000"), *inputs()
        )


def test_confirmatory_analysis_rejects_pilot_and_census_records():
    protocol, design, partition = inputs()
    with pytest.raises(ValueError, match="non-confirmatory"):
        require_confirmatory_records(
            [signed_record("pilot", False, protocol, design, partition)],
            protocol,
            design,
            partition,
        )
    partition = deepcopy(partition)
    partition["confirmatory_subset"]["repetitions"] = 5
    binding = bind_study_assignment(
        "CONF-001",
        assignment("confirmatory", "PW000"),
        protocol,
        design,
        partition,
    )
    require_confirmatory_records(
        [signed_record(binding.phase, True, protocol, design, partition)],
        protocol,
        design,
        partition,
    )


def test_confirmatory_analysis_rejects_tampered_record():
    protocol, design, partition = inputs()
    record = signed_record("confirmatory", True, protocol, design, partition)
    record["study"]["phase"] = "pilot"
    with pytest.raises(ValueError, match="digest mismatch"):
        require_confirmatory_records([record], protocol, design, partition)
