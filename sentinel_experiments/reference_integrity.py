"""Static integrity checks for the verified core bibliography."""

from __future__ import annotations

import json
import re
from pathlib import Path

CITEKEY = re.compile(r"^[a-z][a-z0-9]+$")
BIB_ENTRY = re.compile(r"^@[A-Za-z]+\{([^,]+),", re.MULTILINE)
MANUSCRIPT_CITATION = re.compile(r"@([a-z][a-z0-9]+)")
ALLOWED_STATUS = {"peer-reviewed", "preprint", "government-technical-blog"}


def validate_reference_artifacts(
    ledger_path: Path,
    bib_path: Path,
    manuscript_path: Path | None = None,
) -> int:
    ledger = json.loads(ledger_path.read_text())
    if ledger.get("schema_version") != "sentinel.reference-ledger.v1":
        raise ValueError("unsupported reference ledger schema")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("reference ledger must contain entries")

    citekeys: list[str] = []
    identifiers: list[str] = []
    for entry in entries:
        required = {
            "citekey",
            "title",
            "authors",
            "year",
            "status",
            "venue",
            "identifier",
            "primary_url",
            "relevance",
            "claim_limit",
        }
        missing = required - set(entry)
        if missing:
            raise ValueError(f"reference entry missing fields: {sorted(missing)}")
        citekey = entry["citekey"]
        if not isinstance(citekey, str) or CITEKEY.fullmatch(citekey) is None:
            raise ValueError(f"invalid citekey: {citekey!r}")
        if entry["status"] not in ALLOWED_STATUS:
            raise ValueError(f"invalid publication status for {citekey}")
        if not isinstance(entry["year"], int) or entry["year"] < 1900:
            raise ValueError(f"invalid year for {citekey}")
        if not isinstance(entry["authors"], list) or not entry["authors"]:
            raise ValueError(f"missing authors for {citekey}")
        if not entry["primary_url"].startswith("https://"):
            raise ValueError(f"non-HTTPS primary URL for {citekey}")
        citekeys.append(citekey)
        identifiers.append(entry["identifier"].lower())

    if len(citekeys) != len(set(citekeys)):
        raise ValueError("duplicate citekey")
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate reference identifier")

    bib_keys = BIB_ENTRY.findall(bib_path.read_text())
    if len(bib_keys) != len(set(bib_keys)):
        raise ValueError("duplicate BibTeX citekey")
    if set(bib_keys) != set(citekeys):
        missing_bib = sorted(set(citekeys) - set(bib_keys))
        missing_ledger = sorted(set(bib_keys) - set(citekeys))
        raise ValueError(
            f"ledger/BibTeX mismatch: missing_bib={missing_bib}, "
            f"missing_ledger={missing_ledger}"
        )
    if manuscript_path is not None:
        manuscript_keys = set(MANUSCRIPT_CITATION.findall(manuscript_path.read_text()))
        unknown = sorted(manuscript_keys - set(citekeys))
        if unknown:
            raise ValueError(f"unknown manuscript citekeys: {unknown}")
    return len(entries)
