"""Fail-closed integrity checks for the anonymous submission skeleton."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .contracts import digest

REQUIRED_CLAIMS = {
    "C-NOVELTY",
    "C-SIMULATOR",
    "C-LIVE-SYSTEMS",
    "C-CONFIRMATORY",
    "C-ABLATION",
    "C-ORACLE",
    "C-REPRODUCTION",
    "C-PUBLICATION",
}
RESULT_PLACEHOLDER = re.compile(
    r"\[(?:N|F|PRIMARY RESULT|BASELINE|RESULT|ABLATION|FAILURE MODE|"
    r"EVIDENCE-SUPPORTED CONCLUSION)\]"
)


def check_submission_package(root: Path) -> dict[str, Any]:
    package = root / "paper" / "submission"
    metadata = json.loads((package / "anonymous_metadata.json").read_text())
    ledger = json.loads((package / "claim_evidence.json").read_text())
    manuscript = (root / "paper" / "MANUSCRIPT.md").read_text()
    claims = ledger["claims"]
    claim_ids = [claim["id"] for claim in claims]
    if len(claim_ids) != len(set(claim_ids)) or set(claim_ids) != REQUIRED_CLAIMS:
        raise ValueError("claim/evidence IDs are incomplete or duplicated")
    if metadata["authors"] != ["Anonymous"]:
        raise ValueError("anonymous package contains author metadata")
    for path in package.iterdir():
        if path.is_file() and path.name != "submission_audit.json":
            text = path.read_text()
            if "/Users/" in text or re.search(r"[\w.+-]+@[\w.-]+", text):
                raise ValueError(f"local identity marker in {path.name}")

    statuses: dict[str, int] = {"supported": 0, "partial": 0, "missing": 0}
    for claim in claims:
        status = claim["status"]
        if status not in statuses:
            raise ValueError(f"unsupported claim status: {status}")
        statuses[status] += 1
        if status == "missing" and claim["assertion_allowed"]:
            raise ValueError(f"missing claim marked assertable: {claim['id']}")
        if status == "supported" and claim["evidence_class"] == "none":
            raise ValueError(f"supported claim lacks evidence: {claim['id']}")
    for claim in claims:
        for artifact in claim["artifacts"]:
            if not (root / artifact).is_file():
                raise ValueError(f"claim artifact does not exist: {artifact}")

    checklist_marker = "## Publication-readiness gate"
    if checklist_marker not in manuscript:
        raise ValueError("manuscript publication-readiness gate is missing")
    before_checklist, checklist = manuscript.split(checklist_marker, 1)
    result_tokens = RESULT_PLACEHOLDER.findall(before_checklist)
    result_table_cells = before_checklist.count("[ ]")
    checklist_open = checklist.count("[ ]")
    unresolved = sorted(
        claim["id"] for claim in claims if claim["status"] != "supported"
    )
    ready = (
        metadata["submission_ready"]
        and not result_tokens
        and result_table_cells == 0
        and checklist_open == 0
        and not unresolved
    )
    if ready:
        raise ValueError("skeleton checker cannot certify venue submission readiness")
    report: dict[str, Any] = {
        "schema_version": "sentinel.submission-audit.v1",
        "anonymous_metadata": True,
        "claim_counts": statuses,
        "unresolved_claim_ids": unresolved,
        "result_token_placeholders": len(result_tokens),
        "result_table_placeholders": result_table_cells,
        "open_checklist_items": checklist_open,
        "venue_template_present": False,
        "submission_ready": False,
        "verdict": "honest anonymous skeleton; blocked from submission",
    }
    report["audit_digest"] = digest(report)
    return report
