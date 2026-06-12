import json

from aegis.scenario import default_scenario
from aegis.simulator import run_recorded_simulation
from aegis.telemetry import write_jsonl


def test_recorded_simulation_captures_frames() -> None:
    recorded = run_recorded_simulation(default_scenario(seed=3), seed=3)

    assert recorded.frames
    assert recorded.frames[0].scenario_seed == 3
    assert recorded.frames[0].entities
    assert recorded.result.assets_total == 1


def test_jsonl_trace_export(tmp_path) -> None:
    recorded = run_recorded_simulation(default_scenario(seed=4), seed=4)
    output = tmp_path / "trace.jsonl"

    write_jsonl(recorded.frames[:2], output)

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["scenario_seed"] == 4
