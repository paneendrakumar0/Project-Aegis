from aegis.models import Asset, Drone, DroneRole, Vec2
from aegis.policy import choose_target, hostile_threat_score


def test_ground_attack_inside_threat_range_is_prioritized() -> None:
    asset = Asset("A", Vec2(0, 0))
    friendly = Drone("F1", DroneRole.FRIENDLY, Vec2(100, 0), Vec2(0, 0), 40, 500, 25)
    ground = Drone("HG", DroneRole.HOSTILE_GROUND, Vec2(120, 0), Vec2(-30, 0), 30, 300, 20)
    air = Drone("HA", DroneRole.HOSTILE_AIR, Vec2(80, 0), Vec2(-30, 0), 30, 300, 20)

    decision = choose_target(friendly, (air, ground), (asset,), (friendly,))

    assert decision.hostile_id == "HG"


def test_better_positioned_friendly_reduces_score() -> None:
    asset = Asset("A", Vec2(0, 0))
    far = Drone("F1", DroneRole.FRIENDLY, Vec2(180, 0), Vec2(0, 0), 40, 500, 25)
    near = Drone("F2", DroneRole.FRIENDLY, Vec2(80, 0), Vec2(0, 0), 40, 500, 25)
    hostile = Drone("H1", DroneRole.HOSTILE_GROUND, Vec2(90, 0), Vec2(-30, 0), 30, 300, 20)

    far_score = hostile_threat_score(far, hostile, (asset,), (far, near))
    near_score = hostile_threat_score(near, hostile, (asset,), (far, near))

    assert near_score > far_score

