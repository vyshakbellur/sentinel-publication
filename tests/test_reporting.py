import json

import pytest

from sentinel_experiments.harness import run_matrix
from sentinel_experiments.matrix import initial_matrix
from sentinel_experiments.reporting import summarize, write_run


def test_initial_matrix_exposes_expected_oracle_classes():
    records = run_matrix(initial_matrix())
    summary = summarize(records)
    assert summary["trials"] == 9
    assert summary["unauthorized_effects"] == 4
    assert summary["observation_disagreements"] == 1
    assert any(record.oracle.safe and record.oracle.recovered for record in records)
    assert any(record.oracle.safe and not record.oracle.recovered for record in records)


def test_run_directory_is_write_once(tmp_path):
    output = tmp_path / "run-v1"
    specs = initial_matrix()
    records = run_matrix(specs)
    write_run(output, specs, records)

    lines = (output / "results.jsonl").read_text().splitlines()
    assert len(lines) == len(specs)
    assert all(json.loads(line)["record_digest"] for line in lines)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["schema_version"] == "sentinel.manifest.v2"
    assert manifest["sentinel_sources"]
    assert manifest["manifest_digest"]
    cut_sets = json.loads((output / "cut_sets.json").read_text())
    interaction = next(
        item
        for item in cut_sets["findings"]
        if item["trial_id"] == "guardian-wrong-plus-overbroad-policy"
        and item["outcome"] == "unauthorized_effect"
    )
    assert interaction["minimum_size"] == 2
    assert interaction["minimal_fault_sets"] == [
        ["policy.overbroad_scope", "predictor.wrong_service"]
    ]
    with pytest.raises(FileExistsError):
        write_run(output, specs, records)
