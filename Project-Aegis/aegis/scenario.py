from __future__ import annotations

from random import Random

from aegis.models import Asset, Drone, DroneRole, Scenario, Vec2


def default_scenario(seed: int | None = None, friendly_count: int = 8, hostile_count: int = 10) -> Scenario:
    rng = Random(seed)
    asset = Asset(id="asset-alpha", position=Vec2(500.0, 350.0))

    friendlies = []
    for index in range(friendly_count):
        angle_offset = (index - friendly_count / 2) * 18.0
        friendlies.append(
            Drone(
                id=f"F{index + 1}",
                role=DroneRole.FRIENDLY,
                position=Vec2(500.0 + angle_offset, 435.0 + rng.uniform(-18, 18)),
                velocity=Vec2(0, 0),
                max_speed=42.0,
                sensor_range=360.0,
                engagement_range=28.0,
            )
        )

    hostiles = []
    for index in range(hostile_count):
        side = rng.choice(["north", "south", "east", "west"])
        if side == "north":
            position = Vec2(rng.uniform(80, 920), rng.uniform(20, 80))
        elif side == "south":
            position = Vec2(rng.uniform(80, 920), rng.uniform(620, 680))
        elif side == "east":
            position = Vec2(rng.uniform(920, 980), rng.uniform(80, 620))
        else:
            position = Vec2(rng.uniform(20, 80), rng.uniform(80, 620))

        direction = (asset.position - position).normalized()
        speed = rng.uniform(24.0, 36.0)
        role = DroneRole.HOSTILE_GROUND if rng.random() < 0.62 else DroneRole.HOSTILE_AIR
        hostiles.append(
            Drone(
                id=f"H{index + 1}",
                role=role,
                position=position,
                velocity=direction * speed,
                max_speed=speed,
                sensor_range=300.0,
                engagement_range=22.0,
            )
        )

    return Scenario(assets=(asset,), friendlies=tuple(friendlies), hostiles=tuple(hostiles))

