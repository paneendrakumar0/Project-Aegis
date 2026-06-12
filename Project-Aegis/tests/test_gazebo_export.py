import csv
import xml.etree.ElementTree as ET

from tools.export_gazebo_scene import write_trajectory, write_world


def test_gazebo_export_writes_world_and_trajectory(tmp_path) -> None:
    frames = [
        {
            "time_s": 0.0,
            "entities": [
                {
                    "id": "asset-alpha",
                    "kind": "asset",
                    "role": "protected_ground_asset",
                    "alive": True,
                    "x_m": 500.0,
                    "y_m": 350.0,
                    "z_m": 0.0,
                    "vx_mps": 0.0,
                    "vy_mps": 0.0,
                },
                {
                    "id": "F1",
                    "kind": "drone",
                    "role": "friendly",
                    "alive": True,
                    "x_m": 420.0,
                    "y_m": 430.0,
                    "z_m": 70.0,
                    "vx_mps": 10.0,
                    "vy_mps": 0.0,
                },
            ],
        }
    ]
    world_path = tmp_path / "aegis.world"
    trajectory_path = tmp_path / "trajectory.csv"

    write_world(frames[0], world_path)
    write_trajectory(frames, trajectory_path)

    root = ET.parse(world_path).getroot()
    assert root.tag == "sdf"
    assert len(root.findall("./world/model")) >= 2

    rows = list(csv.DictReader(trajectory_path.open(encoding="utf-8")))
    assert rows
    assert {"time_s", "id", "x_m", "y_m", "z_m", "yaw_rad"}.issubset(rows[0])
