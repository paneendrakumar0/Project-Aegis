from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random

from aegis.models import Asset, Drone, Scenario
from aegis.policy import choose_target, steering_velocity, threatening_range
from aegis.scenario import default_scenario


@dataclass(frozen=True)
class SimulationResult:
    seed: int
    steps: int
    elapsed_time: float
    assets_survived: int
    assets_total: int
    hostiles_neutralized: int
    hostiles_total: int
    friendlies_remaining: int
    friendlies_total: int
    attendance_rate: float

    @property
    def success(self) -> bool:
        return self.assets_survived == self.assets_total and self.hostiles_neutralized == self.hostiles_total


def _resolve_asset_impacts(assets: tuple[Asset, ...], hostiles: tuple[Drone, ...]) -> tuple[Asset, ...]:
    resolved = []
    for asset in assets:
        alive = asset.alive
        for hostile in hostiles:
            if hostile.alive and hostile.ground_attack_capable:
                if hostile.position.distance_to(asset.position) <= asset.radius:
                    alive = False
                    break
        resolved.append(replace(asset, alive=alive))
    return tuple(resolved)


def _resolve_intercepts(friendlies: tuple[Drone, ...], hostiles: tuple[Drone, ...], radius: float) -> tuple[tuple[Drone, ...], int]:
    neutralized = 0
    updated_hostiles = list(hostiles)
    for hostile_index, hostile in enumerate(updated_hostiles):
        if not hostile.alive:
            continue
        for friendly in friendlies:
            if friendly.alive and friendly.position.distance_to(hostile.position) <= max(radius, friendly.engagement_range):
                updated_hostiles[hostile_index] = replace(hostile, alive=False)
                neutralized += 1
                break
    return tuple(updated_hostiles), neutralized


def _attendance_rate(friendlies: tuple[Drone, ...], hostiles: tuple[Drone, ...], assets: tuple[Asset, ...]) -> float:
    threat_count = 0
    attended_count = 0
    for hostile in hostiles:
        if not hostile.alive or not hostile.ground_attack_capable:
            continue
        if not any(hostile.position.distance_to(asset.position) <= threatening_range(hostile) for asset in assets if asset.alive):
            continue
        threat_count += 1
        attended = any(
            friendly.alive and (
                friendly.position.distance_to(hostile.position) <= friendly.engagement_range
                or friendly.position.distance_to(hostile.position) / max(friendly.max_speed, 1.0) <= 10.0
            )
            for friendly in friendlies
        )
        if attended:
            attended_count += 1
    if threat_count == 0:
        return 1.0
    return attended_count / threat_count


def run_simulation(scenario: Scenario, seed: int = 0) -> SimulationResult:
    rng = Random(seed)
    assets = scenario.assets
    friendlies = scenario.friendlies
    hostiles = scenario.hostiles
    neutralized_total = 0
    attendance_samples = []
    steps = int(scenario.max_time / scenario.dt)

    for step in range(steps):
        decisions = {
            friendly.id: choose_target(friendly, hostiles, assets, friendlies)
            for friendly in friendlies
            if friendly.alive
        }

        friendlies = tuple(
            friendly.moved(steering_velocity(friendly, decisions[friendly.id], assets, friendlies), scenario.dt)
            if friendly.alive
            else friendly
            for friendly in friendlies
        )

        jittered_hostiles = []
        for hostile in hostiles:
            if not hostile.alive:
                jittered_hostiles.append(hostile)
                continue
            target_asset = min(assets, key=lambda asset: hostile.position.distance_to(asset.position))
            desired = (target_asset.position - hostile.position).normalized() * hostile.max_speed
            drift = hostile.velocity.normalized() * hostile.max_speed * 0.28
            random_pressure = hostile.velocity.normalized() * rng.uniform(-0.8, 0.8)
            jittered_hostiles.append(hostile.moved((desired * 0.72) + drift + random_pressure, scenario.dt))
        hostiles = tuple(jittered_hostiles)

        assets = _resolve_asset_impacts(assets, hostiles)
        hostiles, neutralized = _resolve_intercepts(friendlies, hostiles, scenario.intercept_radius)
        neutralized_total += neutralized
        attendance_samples.append(_attendance_rate(friendlies, hostiles, assets))

        if not any(asset.alive for asset in assets) or not any(hostile.alive for hostile in hostiles):
            steps = step + 1
            break

    assets_survived = sum(1 for asset in assets if asset.alive)
    hostiles_neutralized = sum(1 for hostile in hostiles if not hostile.alive)
    friendlies_remaining = sum(1 for friendly in friendlies if friendly.alive)
    attendance_rate = sum(attendance_samples) / max(len(attendance_samples), 1)

    return SimulationResult(
        seed=seed,
        steps=steps,
        elapsed_time=steps * scenario.dt,
        assets_survived=assets_survived,
        assets_total=len(assets),
        hostiles_neutralized=hostiles_neutralized,
        hostiles_total=len(hostiles),
        friendlies_remaining=friendlies_remaining,
        friendlies_total=len(friendlies),
        attendance_rate=attendance_rate,
    )


def run_batch(runs: int, seed: int = 0, friendly_count: int = 8, hostile_count: int = 10) -> list[SimulationResult]:
    return [
        run_simulation(
            default_scenario(seed=seed + index, friendly_count=friendly_count, hostile_count=hostile_count),
            seed=seed + index,
        )
        for index in range(runs)
    ]

