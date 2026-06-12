from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector


SCALE = 0.018


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Render Aegis telemetry in Blender.")
    parser.add_argument("--trace", default="reports/baseline-scenario-trace.jsonl")
    parser.add_argument("--out-dir", default="assets/blender")
    parser.add_argument("--fps", type=int, default=8)
    return parser.parse_args(argv)


def load_frames(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def scene_xy(sample: dict) -> tuple[float, float, float]:
    return (
        (float(sample["x_m"]) - 500.0) * SCALE,
        (float(sample["y_m"]) - 350.0) * SCALE,
        float(sample["z_m"]) * SCALE,
    )


def make_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    return material


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def set_render_settings(out_dir: Path, fps: int, frame_count: int) -> None:
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = frame_count
    scene.frame_set(1)
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_gtao = True
    scene.eevee.gtao_distance = 4
    scene.eevee.gtao_factor = 1.2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.fps = fps
    scene.view_settings.view_transform = "Standard"
    if "Medium High Contrast" in scene.view_settings.bl_rna.properties["look"].enum_items:
        scene.view_settings.look = "Medium High Contrast"
    scene.render.image_settings.file_format = "PNG"


def add_environment() -> None:
    bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, -0.02))
    ground = bpy.context.object
    ground.name = "matte tactical ground plane"
    ground.data.materials.append(make_material("ground charcoal", (0.025, 0.032, 0.038, 1)))

    grid_material = make_material("grid line", (0.08, 0.18, 0.22, 1))
    for index in range(-12, 13):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(index, 0, 0.002))
        line = bpy.context.object
        line.name = "grid_x"
        line.dimensions = (0.01, 24, 0.004)
        line.data.materials.append(grid_material)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, index, 0.003))
        line = bpy.context.object
        line.name = "grid_y"
        line.dimensions = (24, 0.01, 0.004)
        line.data.materials.append(grid_material)


def add_asset(sample: dict, material: bpy.types.Material) -> bpy.types.Object:
    x, y, z = scene_xy(sample)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.32, depth=0.22, location=(x, y, z + 0.11))
    asset = bpy.context.object
    asset.name = sample["id"]
    asset.data.materials.append(material)

    bpy.ops.mesh.primitive_torus_add(major_radius=2.1, minor_radius=0.012, location=(x, y, z + 0.025))
    ring = bpy.context.object
    ring.name = f"{sample['id']}_defense_radius"
    ring.data.materials.append(make_material("asset ring", (0.05, 0.85, 0.45, 0.38)))
    return asset


def add_drone(sample: dict, material: bpy.types.Material) -> bpy.types.Object:
    x, y, z = scene_xy(sample)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.18, depth=0.52, location=(x, y, z))
    drone = bpy.context.object
    drone.name = sample["id"]
    drone.rotation_euler[1] = math.radians(90)
    drone.data.materials.append(material)

    rotor_material = make_material(f"{sample['id']}_rotor", (0.02, 0.024, 0.028, 1))
    for offset_x, offset_y in [(0.2, 0.2), (0.2, -0.2), (-0.2, 0.2), (-0.2, -0.2)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.09, depth=0.018, location=(x + offset_x, y + offset_y, z + 0.03))
        rotor = bpy.context.object
        rotor.name = f"{sample['id']}_rotor"
        rotor.data.materials.append(rotor_material)
        rotor.parent = drone
    return drone


def add_trail(samples: list[dict], material: bpy.types.Material, name: str) -> None:
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = 0.012
    polyline = curve.splines.new("POLY")
    polyline.points.add(len(samples) - 1)
    for point, sample in zip(polyline.points, samples):
        x, y, z = scene_xy(sample)
        point.co = (x, y, z, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(material)


def keyframe_entity(obj: bpy.types.Object, samples_by_frame: list[dict]) -> None:
    for frame_index, sample in enumerate(samples_by_frame, start=1):
        x, y, z = scene_xy(sample)
        obj.location = (x, y, z)
        vx = float(sample["vx_mps"])
        vy = float(sample["vy_mps"])
        if vx != 0 or vy != 0:
            obj.rotation_euler[2] = math.atan2(vy, vx)
        obj.hide_viewport = not sample["alive"]
        obj.hide_render = not sample["alive"]
        obj.keyframe_insert(data_path="location", frame=frame_index)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame_index)
        obj.keyframe_insert(data_path="hide_viewport", frame=frame_index)
        obj.keyframe_insert(data_path="hide_render", frame=frame_index)


def add_camera_and_lights() -> None:
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 8))
    sun = bpy.context.object
    sun.name = "low angle sun"
    sun.data.energy = 2.8
    sun.rotation_euler = (math.radians(45), 0, math.radians(35))

    bpy.ops.object.light_add(type="AREA", location=(-4.5, -4.0, 7.0))
    area = bpy.context.object
    area.name = "soft tactical area light"
    area.data.energy = 550
    area.data.size = 6

    bpy.ops.object.camera_add(location=(0, -12.5, 8.5), rotation=(math.radians(58), 0, 0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.data.lens = 32


def add_title() -> None:
    bpy.ops.object.text_add(location=(-6.0, -5.6, 0.05), rotation=(math.radians(70), 0, 0))
    text = bpy.context.object
    text.name = "mission_title"
    text.data.body = "PROJECT AEGIS | TELEMETRY-DRIVEN SWARM SIMULATION"
    text.data.align_x = "LEFT"
    text.data.size = 0.32
    text.data.materials.append(make_material("title white", (0.85, 0.92, 0.96, 1)))


def render(frames: list[dict], out_dir: Path, fps: int) -> None:
    clear_scene()
    out_dir.mkdir(parents=True, exist_ok=True)
    set_render_settings(out_dir, fps, len(frames))
    add_environment()
    add_camera_and_lights()
    add_title()

    materials = {
        "asset": make_material("protected asset green", (0.05, 0.9, 0.45, 1)),
        "friendly": make_material("friendly blue", (0.02, 0.52, 0.95, 1)),
        "hostile_ground": make_material("hostile red", (0.95, 0.04, 0.15, 1)),
        "hostile_air": make_material("hostile amber", (1.0, 0.52, 0.04, 1)),
        "trail_friendly": make_material("trail friendly", (0.0, 0.62, 1.0, 0.55)),
        "trail_hostile": make_material("trail hostile", (1.0, 0.12, 0.18, 0.5)),
    }

    entity_ids = [sample["id"] for sample in frames[0]["entities"]]
    samples = {
        entity_id: [
            next(item for item in frame["entities"] if item["id"] == entity_id)
            for frame in frames
        ]
        for entity_id in entity_ids
    }

    for sample in frames[0]["entities"]:
        if sample["kind"] == "asset":
            add_asset(sample, materials["asset"])
            continue
        material = materials[sample["role"]]
        obj = add_drone(sample, material)
        keyframe_entity(obj, samples[sample["id"]])
        trail_material = materials["trail_friendly"] if sample["role"] == "friendly" else materials["trail_hostile"]
        add_trail(samples[sample["id"]], trail_material, f"{sample['id']}_trajectory")

    bpy.context.scene.frame_set(len(frames) // 2)
    bpy.context.scene.render.filepath = str(out_dir / "aegis_blender_snapshot.png")
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        frame_dir = Path(temp_dir)
        bpy.context.scene.render.image_settings.file_format = "PNG"
        for frame_index in range(1, len(frames) + 1):
            bpy.context.scene.frame_set(frame_index)
            bpy.context.scene.render.filepath = str(frame_dir / f"frame_{frame_index:04d}.png")
            bpy.ops.render.render(write_still=True)

        command = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frame_dir / "frame_%04d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out_dir / "aegis_blender_mission.mp4"),
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(out_dir / "frames", ignore_errors=True)


def main() -> int:
    args = parse_args()
    render(load_frames(Path(args.trace)), Path(args.out_dir), args.fps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
