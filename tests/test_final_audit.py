import hashlib
import json
from pathlib import Path

import pytest

from sentinel_experiments.final_audit import build_report


ROOT = Path(__file__).parents[1]
PROTOCOL_PATH = ROOT / "experiments/protocol/milestone28_final_audit.json"


@pytest.fixture(scope="module")
def protocol():
    return json.loads(PROTOCOL_PATH.read_text())


@pytest.fixture(scope="module")
def reports(protocol):
    return {
        name: json.loads((ROOT / spec["path"]).read_text())
        for name, spec in protocol["source_reports"].items()
    }


@pytest.fixture(scope="module")
def report(protocol, reports):
    content = PROTOCOL_PATH.read_bytes()
    return build_report(protocol, reports, hashlib.sha256(content).hexdigest())


def test_final_audit_accepts_without_claiming_readiness(protocol, report):
    assert report["accepted"]
    assert not report["extracted_evidence"]["publication_ready"]
    for key, expected in protocol["acceptance"].items():
        if key != "accepted":
            assert report["extracted_evidence"][key] == expected


def test_all_publication_gates_remain_fail_closed(report):
    assert len(report["missing_publication_gates"]) == 9
    assert not any(report["publication_gates"].values())
    verdict = report["readiness_verdict"]
    assert not verdict["arxiv_research_preprint_ready"]
    assert not verdict["arr_ready"]
    assert not verdict["q1_or_flagship_ready"]


def test_surviving_claim_is_evaluation_not_guardrail_novelty(report):
    claims = report["claim_decisions"]
    assert claims["deterministic_boundary_novelty"] == "rejected_by_prior_art"
    assert claims["cross_layer_effect_correspondence"].startswith(
        "development_supported"
    )
    assert claims["minimal_cross_layer_assurance_cut_sets"].startswith(
        "development_supported"
    )
    assert claims["nominal_superiority_over_correct_ifc"].startswith("rejected")


def test_heterogeneous_counts_are_never_presented_as_rate(report):
    warning = report["aggregation_warning"]
    assert "never a pooled rate" in warning
    assert report["extracted_evidence"]["descriptive_development_trials"] == 1329


def test_reproduction_grades_preserve_reconstruction_labels(report):
    grades = report["reproduction_grades"]
    assert "conceptual" in grades["fides"]
    assert "zero_of_fourteen" in grades["invitation"]
    assert "not_confirmation" in grades["iteration27_cases"]


def test_report_is_deterministic(protocol, reports, report):
    content = PROTOCOL_PATH.read_bytes()
    assert build_report(protocol, reports, hashlib.sha256(content).hexdigest()) == report
