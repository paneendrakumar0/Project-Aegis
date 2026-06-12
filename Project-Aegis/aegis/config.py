from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aegis.models import Asset, Drone, DroneRole, Scenario, Vec2


class ScenarioConfigError(ValueError):
    """Raised when a scenario manifest cannot be parsed safely."""


def _number(data: dict[str, Any], key: str, default: float | None = None) -> float:
    if key not in data:
        if default is None:
            raise ScenarioConfigError(f"missing required numeric field: {key}")
        return default
    value = data[key]
    if not isinstance(value, int | float):
        raise ScenarioConfigError(f"field {key} must be numeric")
    return float(value)


def _vec2(data: dict[str, Any], key: str) -> Vec2:
    value = data.get(key)
    if not isinstance(value, list | tuple) or len(value) != 2:
        raise ScenarioConfigError(f"field {key} must be a two-number array")
    if not all(isinstance(item, int | float) for item in value):
        raise ScenarioConfigError(f"field {key} must contain only numbers")
    return Vec2(float(value[0]), float(value[1]))


def _asset(data: dict[str, Any]) -> Asset:
    return Asset(
        id=str(data.get("id", "asset")),
        position=_vec2(data, "position_m"),
        radius=_number(data, "radius_m", 18.0),
        altitude_m=_number(data, "altitude_m", 0.0),
    )


def _drone(data: dict[str, Any]) -> Drone:
    try:
        role = DroneRole(str(data["role"]))
    except KeyError as exc:
        raise ScenarioConfigError("drone is missing role") from exc
    except ValueError as exc:
        raise ScenarioConfigError(f"unsupported drone role: {data.get('role')}") from exc

    return Drone(
        id=str(data.get("id", role.value)),
        role=role,
        position=_vec2(data, "position_m"),
        velocity=_vec2(data, "velocity_mps"),
        max_speed=_number(data, "max_speed_mps"),
        sensor_range=_number(data, "sensor_range_m", 360.0),
        engagement_range=_number(data, "engagement_range_m", 28.0),
        altitude_m=_number(data, "altitude_m", 60.0),
        vertical_velocity_mps=_number(data, "vertical_velocity_mps", 0.0),
    )


def load_scenario_config(path: str | Path) -> Scenario:
    config_path = Path(path)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ScenarioConfigError("scenario schema_version must be 1")

    assets = tuple(_asset(item) for item in data.get("assets", []))
    drones = tuple(_drone(item) for item in data.get("drones", []))
    friendlies = tuple(drone for drone in drones if drone.friendly)
    hostiles = tuple(drone for drone in drones if drone.hostile)

    if not assets:
        raise ScenarioConfigError("scenario must define at least one asset")
    if not friendlies:
        raise ScenarioConfigError("scenario must define at least one friendly drone")
    if not hostiles:
        raise ScenarioConfigError("scenario must define at least one hostile drone")

    bounds = data.get("bounds_m", [1000.0, 700.0])
    if not isinstance(bounds, list | tuple) or len(bounds) != 2:
        raise ScenarioConfigError("bounds_m must be a two-number array")

    return Scenario(
        assets=assets,
        friendlies=friendlies,
        hostiles=hostiles,
        bounds=(float(bounds[0]), float(bounds[1])),
        dt=_number(data, "dt_s", 0.5),
        max_time=_number(data, "max_time_s", 120.0),
        intercept_radius=_number(data, "intercept_radius_m", 12.0),
    )
