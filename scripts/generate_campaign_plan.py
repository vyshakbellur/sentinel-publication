"""Expand the checked-in pairwise design across systems and guardrails."""

from __future__ import annotations

import json
from pathlib import Path

from sentinel_experiments.campaign import expand_campaign

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_DIR = ROOT / "experiments" / "protocol"


def main() -> None:
    design = json.loads((PROTOCOL_DIR / "pairwise_design.json").read_text())
    protocol = json.loads(
        (PROTOCOL_DIR / "confirmatory_protocol.json").read_text()
    )
    campaign = expand_campaign(design, protocol)
    output = PROTOCOL_DIR / "campaign_plan.json"
    output.write_text(json.dumps(campaign, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(campaign['rows'])} unique campaign rows")


if __name__ == "__main__":
    main()
