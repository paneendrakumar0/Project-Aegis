from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from math import hypot


class DroneRole(str, Enum):
    FRIENDLY = "friendly"
    HOSTILE_AIR = "hostile_air"
    HOSTILE_GROUND = "hostile_ground"


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def length(self) -> float:
        return hypot(self.x, self.y)

    def distance_to(self, other: Vec2) -> float:
        return (self - other).length()

    def normalized(self) -> Vec2:
        length = self.length()
        if length == 0:
            return Vec2(0, 0)
        return Vec2(self.x / length, self.y / length)

    def limit(self, max_length: float) -> Vec2:
        length = self.length()
        if length <= max_length or length == 0:
            return self
        return self.normalized() * max_length


@dataclass(frozen=True)
class Asset:
    id: str
    position: Vec2
    radius: float = 18.0
    altitude_m: float = 0.0
    alive: bool = True


@dataclass(frozen=True)
class Drone:
    id: str
    role: DroneRole
    position: Vec2
    velocity: Vec2
    max_speed: float
    sensor_range: float
    engagement_range: float
    altitude_m: float = 60.0
    vertical_velocity_mps: float = 0.0
    alive: bool = True

    @property
    def ground_attack_capable(self) -> bool:
        return self.role == DroneRole.HOSTILE_GROUND

    @property
    def hostile(self) -> bool:
        return self.role in {DroneRole.HOSTILE_AIR, DroneRole.HOSTILE_GROUND}

    @property
    def friendly(self) -> bool:
        return self.role == DroneRole.FRIENDLY

    def moved(self, velocity: Vec2, dt: float) -> Drone:
        bounded_velocity = velocity.limit(self.max_speed)
        return replace(self, velocity=bounded_velocity, position=self.position + bounded_velocity * dt)


@dataclass(frozen=True)
class Scenario:
    assets: tuple[Asset, ...]
    friendlies: tuple[Drone, ...]
    hostiles: tuple[Drone, ...]
    bounds: tuple[float, float] = (1000.0, 700.0)
    dt: float = 0.5
    max_time: float = 120.0
    intercept_radius: float = 12.0
