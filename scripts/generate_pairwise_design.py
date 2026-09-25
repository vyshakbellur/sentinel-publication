"""Generate the frozen pairwise design from the protocol and fault catalog."""

from __future__ import annotations

import json
from pathlib import Path

from sentinel_experiments.design import generate_pairwise_design

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_DIR = ROOT / "experiments" / "protocol"


def main() -> None:
    catalog = json.loads((PROTOCOL_DIR / "fault_catalog.json").read_text())
    protocol = json.loads(
        (PROTOCOL_DIR / "confirmatory_protocol.json").read_text()
    )
    design = generate_pairwise_design(catalog, protocol)
    output = PROTOCOL_DIR / "pairwise_design.json"
    output.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(
        f"wrote {len(design['rows'])} rows; "
        f"{design['coverage']['cross_layer_pairs_covered']} pairs covered; "
        f"{design['trial_budget_per_repetition']} trials/repetition"
    )


if __name__ == "__main__":
    main()
