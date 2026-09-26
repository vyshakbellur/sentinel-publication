import json
from dataclasses import dataclass
from pathlib import Path

from sentinel_experiments.scheduling import (
    audit_pilot_schedule,
    blind_pilot_schedule,
    execute_schedule,
    generate_pilot_schedule,
)

ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "experiments" / "protocol"


def inputs():
    protocol = json.loads((PROTOCOL / "confirmatory_protocol.json").read_text())
    design = json.loads((PROTOCOL / "pairwise_design.json").read_text())
    partition = json.loads((PROTOCOL / "study_partition.json").read_text())
    blocks = json.loads((PROTOCOL / "pilot_blocks_contract.json").read_text())
    return protocol, design, partition, blocks


def test_checked_schedule_is_complete_balanced_and_reproducible():
    protocol, design, partition, blocks = inputs()
    first = generate_pilot_schedule(protocol, design, partition, blocks)
    second = generate_pilot_schedule(protocol, design, partition, blocks)
    checked = json.loads((PROTOCOL / "pilot_schedule_contract.json").read_text())
    audit = json.loads((PROTOCOL / "pilot_schedule_contract_audit.json").read_text())
    assert first == second == checked
    assert audit == audit_pilot_schedule(first, protocol, design, partition)
    assert audit["rows"] == 360
    assert audit["rows_per_system_block"] == [60]
    assert audit["repetitions_per_system_guardrail_row"] == 3
    assert not audit["confirmatory_eligible"]


def test_blinded_schedule_excludes_guardrail_labels_and_keys():
    protocol, design, partition, blocks = inputs()
    schedule = generate_pilot_schedule(protocol, design, partition, blocks)
    blinded = blind_pilot_schedule(schedule, b"test-only-secret")
    assert len(blinded["rows"]) == len(schedule["rows"])
    assert all("guardrail" not in row for row in blinded["rows"])
    assert all("randomization_key" not in row for row in blinded["rows"])
    assert len({row["condition_token"] for row in blinded["rows"]}) == 360


@dataclass(frozen=True)
class Outcome:
    succeeded: bool


def test_schedule_stops_immediately_after_failed_terminal_record():
    schedule = {
        "rows": [
            {"trial_id": "PILOT-001"},
            {"trial_id": "PILOT-002"},
            {"trial_id": "PILOT-003"},
        ]
    }
    outcomes = iter((Outcome(True), Outcome(False), Outcome(True)))
    result = execute_schedule(schedule, lambda _row: next(outcomes))
    assert result.attempted_trial_ids == ("PILOT-001", "PILOT-002")
    assert not result.completed
    assert result.stopped_at_trial_id == "PILOT-002"
