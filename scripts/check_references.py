"""Validate the verified core reference ledger against its BibTeX file."""

from pathlib import Path

from sentinel_experiments.reference_integrity import validate_reference_artifacts

ROOT = Path(__file__).parents[1]


def main() -> int:
    count = validate_reference_artifacts(
        ROOT / "references/core_references.json",
        ROOT / "paper/references.bib",
        ROOT / "paper/MANUSCRIPT.md",
    )
    print(f"verified reference artifacts: {count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
