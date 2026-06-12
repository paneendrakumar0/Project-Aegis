from aegis.scenario import default_scenario
from aegis.simulator import run_batch, run_simulation


def test_simulation_is_deterministic_for_seed() -> None:
    first = run_simulation(default_scenario(seed=7), seed=7)
    second = run_simulation(default_scenario(seed=7), seed=7)

    assert first == second


def test_batch_returns_requested_runs() -> None:
    results = run_batch(3, seed=10)

    assert len(results) == 3
    assert all(0.0 <= result.attendance_rate <= 1.0 for result in results)

