from __future__ import annotations

from dataclasses import dataclass
from math import inf

from aegis.models import Asset, Drone, DroneRole, Vec2


@dataclass(frozen=True)
class TargetDecision:
    friendly_id: str
    hostile_id: str | None
    score: float
    intercept_point: Vec2 | None


def nearest_asset(hostile: Drone, assets: tuple[Asset, ...]) -> Asset | None:
    live_assets = [asset for asset in assets if asset.alive]
    if not live_assets:
        return None
    return min(live_assets, key=lambda asset: hostile.position.distance_to(asset.position))


def time_to_asset(hostile: Drone, asset: Asset) -> float:
    closing_speed = max(hostile.max_speed, hostile.velocity.length(), 1.0)
    return hostile.position.distance_to(asset.position) / closing_speed


def threatening_range(hostile: Drone) -> float:
    return 10.0 * max(hostile.max_speed, hostile.velocity.length())


def predict_intercept_point(friendly: Drone, hostile: Drone, horizon: float = 8.0) -> Vec2:
    distance = friendly.position.distance_to(hostile.position)
    relative_speed = max(friendly.max_speed + hostile.velocity.length(), 1.0)
    lead_time = min(horizon, distance / relative_speed)
    return hostile.position + hostile.velocity * lead_time


def hostile_threat_score(
    friendly: Drone,
    hostile: Drone,
    assets: tuple[Asset, ...],
    friendlies: tuple[Drone, ...],
) -> float:
    if not friendly.alive or not hostile.alive:
        return -inf

    asset = nearest_asset(hostile, assets)
    if asset is None:
        return -inf

    asset_distance = hostile.position.distance_to(asset.position)
    friendly_distance = friendly.position.distance_to(hostile.position)
    seconds_to_asset = time_to_asset(hostile, asset)
    within_threatening_range = asset_distance <= threatening_range(hostile)

    role_weight = 2.2 if hostile.role == DroneRole.HOSTILE_GROUND else 1.0
    urgency = 1.0 / max(seconds_to_asset, 0.5)
    proximity = 1.0 / max(asset_distance, 1.0)
    intercept_cost = friendly_distance / max(friendly.max_speed, 1.0)

    score = (role_weight * 180.0 * urgency) + (80.0 * proximity) - (0.45 * intercept_cost)
    if within_threatening_range and hostile.ground_attack_capable:
        score += 35.0

    better_positioned_friendlies = 0
    for other in friendlies:
        if other.id == friendly.id or not other.alive:
            continue
        if other.position.distance_to(hostile.position) + 20.0 < friendly_distance:
            better_positioned_friendlies += 1

    return score - (better_positioned_friendlies * 8.0)


def choose_target(
    friendly: Drone,
    hostiles: tuple[Drone, ...],
    assets: tuple[Asset, ...],
    friendlies: tuple[Drone, ...],
) -> TargetDecision:
    visible_hostiles = [
        hostile
        for hostile in hostiles
        if hostile.alive and friendly.position.distance_to(hostile.position) <= friendly.sensor_range
    ]
    if not visible_hostiles:
        return TargetDecision(friendly.id, None, 0.0, None)

    scored = [
        (hostile_threat_score(friendly, hostile, assets, friendlies), hostile)
        for hostile in visible_hostiles
    ]
    score, hostile = max(scored, key=lambda item: item[0])
    if score == -inf:
        return TargetDecision(friendly.id, None, 0.0, None)

    return TargetDecision(
        friendly_id=friendly.id,
        hostile_id=hostile.id,
        score=score,
        intercept_point=predict_intercept_point(friendly, hostile),
    )


def steering_velocity(
    friendly: Drone,
    decision: TargetDecision,
    assets: tuple[Asset, ...],
    friendlies: tuple[Drone, ...],
) -> Vec2:
    if decision.intercept_point is None:
        home = assets[0].position if assets else Vec2(0, 0)
        desired = (home - friendly.position).normalized() * (friendly.max_speed * 0.45)
    else:
        desired = (decision.intercept_point - friendly.position).normalized() * friendly.max_speed

    separation = Vec2(0, 0)
    for other in friendlies:
        if other.id == friendly.id or not other.alive:
            continue
        distance = friendly.position.distance_to(other.position)
        if 0 < distance < 35.0:
            separation = separation + (friendly.position - other.position).normalized() * ((35.0 - distance) / 35.0)

    return (desired + separation * friendly.max_speed * 0.35).limit(friendly.max_speed)

