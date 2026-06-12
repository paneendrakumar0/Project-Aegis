from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from aegis.models import Asset, Drone


@dataclass(frozen=True)
class EntitySample:
    id: str
    kind: str
    role: str
    alive: bool
    x_m: float
    y_m: float
    z_m: float
    vx_mps: float
    vy_mps: float
    vz_mps: float


@dataclass(frozen=True)
class TelemetryFrame:
    scenario_seed: int
    frame_index: int
    time_s: float
    assets_alive: int
    hostiles_alive: int
    friendlies_alive: int
    attendance_rate: float
    entities: tuple[EntitySample, ...]


def sample_asset(asset: Asset) -> EntitySample:
    return EntitySample(
        id=asset.id,
        kind="asset",
        role="protected_ground_asset",
        alive=asset.alive,
        x_m=asset.position.x,
        y_m=asset.position.y,
        z_m=0.0,
        vx_mps=0.0,
        vy_mps=0.0,
        vz_mps=0.0,
    )


def sample_drone(drone: Drone) -> EntitySample:
    return EntitySample(
        id=drone.id,
        kind="drone",
        role=drone.role.value,
        alive=drone.alive,
        x_m=drone.position.x,
        y_m=drone.position.y,
        z_m=60.0,
        vx_mps=drone.velocity.x,
        vy_mps=drone.velocity.y,
        vz_mps=0.0,
    )


def capture_frame(
    scenario_seed: int,
    frame_index: int,
    time_s: float,
    assets: tuple[Asset, ...],
    friendlies: tuple[Drone, ...],
    hostiles: tuple[Drone, ...],
    attendance_rate: float,
) -> TelemetryFrame:
    entities = tuple(
        [sample_asset(asset) for asset in assets]
        + [sample_drone(drone) for drone in friendlies]
        + [sample_drone(drone) for drone in hostiles]
    )
    return TelemetryFrame(
        scenario_seed=scenario_seed,
        frame_index=frame_index,
        time_s=time_s,
        assets_alive=sum(1 for asset in assets if asset.alive),
        hostiles_alive=sum(1 for hostile in hostiles if hostile.alive),
        friendlies_alive=sum(1 for friendly in friendlies if friendly.alive),
        attendance_rate=attendance_rate,
        entities=entities,
    )


def write_jsonl(frames: list[TelemetryFrame], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        for frame in frames:
            output_file.write(json.dumps(asdict(frame), separators=(",", ":")) + "\n")

