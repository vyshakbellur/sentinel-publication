import json
from pathlib import Path

import pytest

from sentinel_experiments.reference_integrity import validate_reference_artifacts

ROOT = Path(__file__).parents[1]


def test_checked_in_reference_ledger_matches_bibtex():
    count = validate_reference_artifacts(
        ROOT / "references/core_references.json",
        ROOT / "paper/references.bib",
        ROOT / "paper/MANUSCRIPT.md",
    )
    assert count == 31


def test_duplicate_identifier_fails_closed(tmp_path):
    source = ROOT / "references/core_references.json"
    ledger = json.loads(source.read_text())
    ledger["entries"][1]["identifier"] = ledger["entries"][0]["identifier"]
    duplicate = tmp_path / "references.json"
    duplicate.write_text(json.dumps(ledger))
    with pytest.raises(ValueError, match="duplicate reference identifier"):
        validate_reference_artifacts(duplicate, ROOT / "paper/references.bib")


def test_unknown_manuscript_citation_fails_closed(tmp_path):
    manuscript = tmp_path / "manuscript.md"
    manuscript.write_text("Unsupported citation [@notintheledger].\n")
    with pytest.raises(ValueError, match="unknown manuscript citekeys"):
        validate_reference_artifacts(
            ROOT / "references/core_references.json",
            ROOT / "paper/references.bib",
            manuscript,
        )
