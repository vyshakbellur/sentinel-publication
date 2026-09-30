import json
from copy import deepcopy
from pathlib import Path

import pytest

from sentinel_experiments.submission_integrity import check_submission_package

ROOT = Path(__file__).parents[1]


def test_checked_submission_audit_matches_honest_non_readiness_state():
    report = check_submission_package(ROOT)
    checked = json.loads(
        (ROOT / "paper/submission/submission_audit.json").read_text()
    )
    assert report == checked
    assert not report["submission_ready"]
    assert report["claim_counts"] == {
        "supported": 2,
        "partial": 3,
        "missing": 3,
    }
    # The development paper now reports bounded results; the unexecuted
    # archival study is identified explicitly rather than with bracket tokens.
    assert report["result_token_placeholders"] == 0
    assert report["result_table_placeholders"] == 0
    assert report["open_checklist_items"] > 0


def test_missing_claim_cannot_be_marked_assertable(tmp_path):
    package = tmp_path / "paper" / "submission"
    package.mkdir(parents=True)
    source = ROOT / "paper" / "submission"
    for name in ("anonymous_metadata.json", "claim_evidence.json", "README.md"):
        (package / name).write_text((source / name).read_text())
    (package / "ARTIFACT_APPENDIX.md").write_text(
        (source / "ARTIFACT_APPENDIX.md").read_text()
    )
    manuscript = tmp_path / "paper" / "MANUSCRIPT.md"
    manuscript.write_text((ROOT / "paper" / "MANUSCRIPT.md").read_text())
    ledger_path = package / "claim_evidence.json"
    ledger = json.loads(ledger_path.read_text())
    broken = deepcopy(ledger)
    next(claim for claim in broken["claims"] if claim["status"] == "missing")[
        "assertion_allowed"
    ] = True
    ledger_path.write_text(json.dumps(broken))
    with pytest.raises(ValueError, match="missing claim marked assertable"):
        check_submission_package(tmp_path)
