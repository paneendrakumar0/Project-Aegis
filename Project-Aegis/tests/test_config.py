from aegis.config import load_scenario_config


def test_load_baseline_scenario_config() -> None:
    scenario = load_scenario_config("scenarios/baseline_asset_defense.json")

    assert scenario.assets[0].id == "asset-alpha"
    assert len(scenario.friendlies) == 6
    assert len(scenario.hostiles) == 4
    assert scenario.friendlies[0].altitude_m == 70.0
