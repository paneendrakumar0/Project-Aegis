from __future__ import annotations

import argparse
import csv
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom


def load_frames(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def yaw_from_velocity(sample: dict) -> float:
    vx = float(sample["vx_mps"])
    vy = float(sample["vy_mps"])
    if vx == 0 and vy == 0:
        return 0.0
    return math.atan2(vy, vx)


def color_for_role(role: str) -> str:
    if role == "friendly":
        return "0.04 0.55 0.95 1"
    if role == "hostile_ground":
        return "0.95 0.05 0.18 1"
    if role == "hostile_air":
        return "1.0 0.55 0.05 1"
    return "0.2 0.9 0.55 1"


def add_text(parent: ET.Element, name: str, text: str) -> ET.Element:
    child = ET.SubElement(parent, name)
    child.text = text
    return child


def add_drone_model(world: ET.Element, sample: dict) -> None:
    model = ET.SubElement(world, "model", {"name": sample["id"]})
    add_text(model, "pose", f"{sample['x_m']} {sample['y_m']} {sample['z_m']} 0 0 {yaw_from_velocity(sample)}")
    add_text(model, "static", "false")
    link = ET.SubElement(model, "link", {"name": "base_link"})
    add_text(link, "gravity", "false")

    body_visual = ET.SubElement(link, "visual", {"name": "body"})
    add_text(body_visual, "pose", "0 0 0 0 0 0")
    geometry = ET.SubElement(body_visual, "geometry")
    box = ET.SubElement(geometry, "box")
    add_text(box, "size", "6 1.2 0.35")
    material = ET.SubElement(body_visual, "material")
    add_text(material, "ambient", color_for_role(sample["role"]))
    add_text(material, "diffuse", color_for_role(sample["role"]))

    for index, (x, y) in enumerate([(2.2, 2.2), (2.2, -2.2), (-2.2, 2.2), (-2.2, -2.2)]):
        rotor = ET.SubElement(link, "visual", {"name": f"rotor_{index + 1}"})
        add_text(rotor, "pose", f"{x} {y} 0 0 0 0")
        rotor_geometry = ET.SubElement(rotor, "geometry")
        cylinder = ET.SubElement(rotor_geometry, "cylinder")
        add_text(cylinder, "radius", "0.75")
        add_text(cylinder, "length", "0.06")
        rotor_material = ET.SubElement(rotor, "material")
        add_text(rotor_material, "ambient", "0.08 0.09 0.1 1")
        add_text(rotor_material, "diffuse", "0.08 0.09 0.1 1")


def add_asset_model(world: ET.Element, sample: dict) -> None:
    model = ET.SubElement(world, "model", {"name": sample["id"]})
    add_text(model, "pose", f"{sample['x_m']} {sample['y_m']} 0 0 0 0")
    add_text(model, "static", "true")
    link = ET.SubElement(model, "link", {"name": "base_link"})
    visual = ET.SubElement(link, "visual", {"name": "protected_asset"})
    geometry = ET.SubElement(visual, "geometry")
    cylinder = ET.SubElement(geometry, "cylinder")
    add_text(cylinder, "radius", "14")
    add_text(cylinder, "length", "8")
    material = ET.SubElement(visual, "material")
    add_text(material, "ambient", "0.1 0.85 0.45 1")
    add_text(material, "diffuse", "0.1 0.85 0.45 1")


def write_world(first_frame: dict, path: Path) -> None:
    sdf = ET.Element("sdf", {"version": "1.6"})
    world = ET.SubElement(sdf, "world", {"name": "aegis_baseline"})
    add_text(world, "gravity", "0 0 -9.8")
    add_text(world, "magnetic_field", "6e-06 2.3e-05 -4.2e-05")

    include_sun = ET.SubElement(world, "include")
    add_text(include_sun, "uri", "model://sun")
    include_ground = ET.SubElement(world, "include")
    add_text(include_ground, "uri", "model://ground_plane")

    scene = ET.SubElement(world, "scene")
    add_text(scene, "ambient", "0.38 0.42 0.46 1")
    add_text(scene, "background", "0.025 0.032 0.04 1")
    add_text(scene, "shadows", "true")

    for sample in first_frame["entities"]:
        if sample["kind"] == "asset":
            add_asset_model(world, sample)
        elif sample["kind"] == "drone":
            add_drone_model(world, sample)

    rough = ET.tostring(sdf, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty, encoding="utf-8")


def write_trajectory(frames: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["time_s", "id", "kind", "role", "alive", "x_m", "y_m", "z_m", "yaw_rad"],
        )
        writer.writeheader()
        for frame in frames:
            for sample in frame["entities"]:
                writer.writerow(
                    {
                        "time_s": frame["time_s"],
                        "id": sample["id"],
                        "kind": sample["kind"],
                        "role": sample["role"],
                        "alive": sample["alive"],
                        "x_m": sample["x_m"],
                        "y_m": sample["y_m"],
                        "z_m": sample["z_m"],
                        "yaw_rad": yaw_from_velocity(sample),
                    }
                )


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Aegis telemetry to Gazebo scene artifacts.")
    parser.add_argument("--trace", default="reports/baseline-scenario-trace.jsonl")
    parser.add_argument("--world", default="integrations/gazebo/worlds/aegis_baseline.world")
    parser.add_argument("--trajectory", default="integrations/gazebo/trajectories/aegis_baseline_trajectory.csv")
    args = parser.parse_args()

    frames = load_frames(Path(args.trace))
    if not frames:
        raise SystemExit("trace has no frames")
    write_world(frames[0], Path(args.world))
    write_trajectory(frames, Path(args.trajectory))
    print(f"wrote Gazebo world: {args.world}")
    print(f"wrote trajectory CSV: {args.trajectory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
