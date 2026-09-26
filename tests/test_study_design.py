import json
from copy import deepcopy
from pathlib import Path

import pytest

from sentinel_experiments.study_design import audit_study_partition

ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments" / "protocol"


def inputs():
    design = json.loads((PROTOCOL / "pairwise_design.json").read_text())
    confirmatory = json.loads((PROTOCOL / "confirmatory_protocol.json").read_text())
    partition = json.loads((PROTOCOL / "study_partition.json").read_text())
    return design, confirmatory, partition


def test_study_partition_separates_coverage_from_inference():
    report = audit_study_partition(*inputs())
    assert report["rows"] == {
        "frozen_design": 58,
        "pilot": 12,
        "census": 58,
        "confirmatory": 19,
        "confirmatory_pairs": 7,
    }
    assert report["cells_per_complete_block"] == {
        "pilot": 120,
        "census": 580,
        "confirmatory": 190,
    }
    assert report["selected_pair_layers"] == [
        "binding",
        "enforcement",
        "evidence",
        "observation",
        "policy",
        "predictor",
    ]
    assert not report["phase_record_reuse"]
    assert report["pilot_condition_labels_masked"]
    assert report["primary_inference_phases"] == ["confirmatory"]


def test_selected_interaction_requires_both_component_singles():
    design, confirmatory, partition = inputs()
    broken = deepcopy(partition)
    broken["confirmatory_subset"]["row_ids"].remove("PW005")
    with pytest.raises(ValueError, match="nominal and all singles"):
        audit_study_partition(design, confirmatory, broken)


def test_checked_in_audit_matches_protocol():
    checked = json.loads((PROTOCOL / "study_partition_audit.json").read_text())
    assert checked == audit_study_partition(*inputs())
