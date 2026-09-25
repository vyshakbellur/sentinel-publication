import json
from pathlib import Path

import pytest

from sentinel_experiments.run_analysis import (
    analyze_run,
    clopper_pearson,
    verify_run,
)

ROOT = Path(__file__).parents[1]
RUN = ROOT / "experiments/runs/e3-campaign-preflight-v1"


def test_clopper_pearson_handles_zero_and_all_events():
    zero = clopper_pearson(0, 10)
    all_events = clopper_pearson(10, 10)
    assert zero[0] == 0.0 and 0.0 < zero[1] < 1.0
    assert 0.0 < all_events[0] < 1.0 and all_events[1] == 1.0


def test_preflight_integrity_and_boundary_are_machine_checked():
    manifest, records = verify_run(RUN)
    assert manifest["manifest_digest"]
    assert len(records) == 580
    report = analyze_run(RUN)
    assert report["integrity"]["manifest_and_record_digests_verified"]
    assert report["evidence_class"] == "simulator_preflight"
    assert not report["confirmatory_eligible"]


def test_simulator_run_is_rejected_as_confirmatory_evidence():
    with pytest.raises(ValueError, match="ineligible for confirmatory"):
        analyze_run(RUN, confirmatory=True)


def test_preflight_contrasts_are_paired_and_labeled():
    report = analyze_run(RUN)
    assert report["preflight_contrasts"]["C1"]["paired_rows"] > 0
    assert report["preflight_contrasts"]["C2"]["paired_rows"] > 0
    assert report["preflight_contrasts"]["C5"]["paired_rows"] == 116


def test_checked_in_preflight_report_matches_verified_records():
    checked_in = json.loads((RUN / "preflight_analysis.json").read_text())
    assert checked_in == analyze_run(RUN)
