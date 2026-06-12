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
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.72
        if color[3] < 1:
            bsdf.inputs["Alpha"].default_value = color[3]
            material.blend_method = "BLEND"
            material.use_screen_refraction = True
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
    bpy.ops.mesh.primitive_plane_add(size=34, location=(0, 0, -0.04))
    ground = bpy.context.object
    ground.name = "semi arid operational theater"
    ground.data.materials.append(make_material("dusty terrain", (0.16, 0.15, 0.13, 1)))

    grid_material = make_material("subtle coordinate grid", (0.05, 0.13, 0.14, 1))
    for index in range(-16, 17):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(index, 0, 0.002))
        line = bpy.context.object
        line.name = "grid_x"
        line.dimensions = (0.006, 34, 0.004)
        line.data.materials.append(grid_material)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, index, 0.003))
        line = bpy.context.object
        line.name = "grid_y"
        line.dimensions = (34, 0.006, 0.004)
        line.data.materials.append(grid_material)

    road_material = make_material("service road asphalt", (0.075, 0.075, 0.07, 1))
    for location, dimensions, rotation in [
        ((0, -1.35, 0.01), (16, 0.38, 0.02), 0),
        ((-2.4, 0.5, 0.012), (0.36, 7.6, 0.02), math.radians(13)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=(0, 0, rotation))
        road = bpy.context.object
        road.name = "service road"
        road.dimensions = dimensions
        road.data.materials.append(road_material)

    building_material = make_material("reinforced concrete", (0.34, 0.35, 0.32, 1))
    roof_material = make_material("dark roof", (0.08, 0.085, 0.08, 1))
    for x, y, sx, sy, sz in [
        (-1.25, -0.25, 0.9, 0.65, 0.35),
        (1.05, -0.55, 1.1, 0.55, 0.32),
        (0.25, 0.85, 0.72, 0.75, 0.28),
        (-2.15, 0.95, 0.58, 0.48, 0.24),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, sz / 2))
        building = bpy.context.object
        building.name = "protected installation structure"
        building.dimensions = (sx, sy, sz)
        building.data.materials.append(building_material)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, sz + 0.025))
        roof = bpy.context.object
        roof.name = "low observable roof"
        roof.dimensions = (sx + 0.08, sy + 0.08, 0.05)
        roof.data.materials.append(roof_material)

    wall_material = make_material("perimeter wall", (0.26, 0.27, 0.24, 1))
    for location, dimensions in [
        ((0, 1.95, 0.16), (5.4, 0.12, 0.32)),
        ((0, -1.95, 0.16), (5.4, 0.12, 0.32)),
        ((2.7, 0, 0.16), (0.12, 4.0, 0.32)),
        ((-2.7, 0, 0.16), (0.12, 4.0, 0.32)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        wall = bpy.context.object
        wall.name = "compound perimeter wall"
        wall.dimensions = dimensions
        wall.data.materials.append(wall_material)

    mast_material = make_material("sensor mast", (0.16, 0.17, 0.17, 1))
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.035, depth=1.15, location=(2.15, 1.35, 0.58))
    mast = bpy.context.object
    mast.name = "radar sensor mast"
    mast.data.materials.append(mast_material)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.18, location=(2.15, 1.35, 1.2))
    dome = bpy.context.object
    dome.name = "sensor radome"
    dome.data.materials.append(make_material("radome white", (0.75, 0.78, 0.76, 1)))


def add_asset(sample: dict, material: bpy.types.Material) -> bpy.types.Object:
    x, y, z = scene_xy(sample)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.22, depth=0.18, location=(x, y, z + 0.11))
    asset = bpy.context.object
    asset.name = sample["id"]
    asset.data.materials.append(material)

    bpy.ops.mesh.primitive_torus_add(major_radius=2.15, minor_radius=0.008, location=(x, y, z + 0.035))
    ring = bpy.context.object
    ring.name = f"{sample['id']}_defense_radius"
    ring.data.materials.append(make_material("asset protected radius", (0.05, 0.85, 0.45, 0.24)))
    return asset


def parent_keep_transform(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def add_arm(root: bpy.types.Object, name: str, location: tuple[float, float, float], rotation_z: float, material: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=(0, 0, rotation_z))
    arm = bpy.context.object
    arm.name = name
    arm.dimensions = (0.62, 0.045, 0.035)
    arm.data.materials.append(material)
    parent_keep_transform(arm, root)


def add_rotor(root: bpy.types.Object, name: str, location: tuple[float, float, float], material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.13, depth=0.018, location=location)
    rotor = bpy.context.object
    rotor.name = name
    rotor.data.materials.append(material)
    parent_keep_transform(rotor, root)
    return rotor


def add_drone(sample: dict, accent_material: bpy.types.Material, body_material: bpy.types.Material) -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    x, y, z = scene_xy(sample)
    root = bpy.data.objects.new(sample["id"], None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.25
    root.location = (x, y, z)

    children: list[bpy.types.Object] = []
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    body = bpy.context.object
    body.name = f"{sample['id']}_fuselage"
    body.dimensions = (0.42, 0.18, 0.12)
    body.data.materials.append(body_material)
    parent_keep_transform(body, root)
    children.append(body)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.075, location=(x + 0.24, y, z + 0.015))
    nose = bpy.context.object
    nose.name = f"{sample['id']}_sensor_nose"
    nose.data.materials.append(accent_material)
    parent_keep_transform(nose, root)
    children.append(nose)

    for angle in [math.radians(35), math.radians(-35), math.radians(145), math.radians(-145)]:
        add_arm(root, f"{sample['id']}_carbon_arm", (x, y, z), angle, body_material)

    rotor_material = make_material(f"{sample['id']}_rotor_blur", (0.015, 0.018, 0.018, 0.72))
    rotor_offsets = [(0.32, 0.32), (0.32, -0.32), (-0.32, 0.32), (-0.32, -0.32)]
    for index, (offset_x, offset_y) in enumerate(rotor_offsets, start=1):
        rotor = add_rotor(root, f"{sample['id']}_rotor_{index}", (x + offset_x, y + offset_y, z + 0.04), rotor_material)
        children.append(rotor)

    return root, children


def add_trail(samples: list[dict], material: bpy.types.Material, name: str) -> None:
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = 0.006
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


def keyframe_drone(root: bpy.types.Object, children: list[bpy.types.Object], samples_by_frame: list[dict]) -> None:
    for frame_index, sample in enumerate(samples_by_frame, start=1):
        x, y, z = scene_xy(sample)
        root.location = (x, y, z)
        vx = float(sample["vx_mps"])
        vy = float(sample["vy_mps"])
        if vx != 0 or vy != 0:
            root.rotation_euler[2] = math.atan2(vy, vx)
        root.keyframe_insert(data_path="location", frame=frame_index)
        root.keyframe_insert(data_path="rotation_euler", frame=frame_index)
        for child in children:
            if "rotor" in child.name:
                child.rotation_euler[2] = frame_index * math.radians(55)
                child.keyframe_insert(data_path="rotation_euler", frame=frame_index)
            child.hide_viewport = not sample["alive"]
            child.hide_render = not sample["alive"]
            child.keyframe_insert(data_path="hide_viewport", frame=frame_index)
            child.keyframe_insert(data_path="hide_render", frame=frame_index)


def add_neutralization_markers(samples_by_entity: dict[str, list[dict]], material: bpy.types.Material) -> None:
    for entity_id, samples in samples_by_entity.items():
        if not entity_id.startswith("H"):
            continue
        alive_samples = [sample for sample in samples if sample["alive"]]
        if not alive_samples or alive_samples[-1] is samples[-1]:
            continue
        x, y, z = scene_xy(alive_samples[-1])
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.28, location=(x, y, z))
        marker = bpy.context.object
        marker.name = f"{entity_id}_disabled_marker"
        marker.scale = (1, 1, 0.45)
        marker.data.materials.append(material)


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

    bpy.ops.object.camera_add(location=(0.2, -13.8, 8.4), rotation=(math.radians(58), 0, math.radians(2)))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.data.lens = 32


def add_title() -> None:
    bpy.ops.object.text_add(location=(-5.8, -4.8, 0.05), rotation=(math.radians(70), 0, 0))
    text = bpy.context.object
    text.name = "mission_title"
    text.data.body = "PROJECT AEGIS | DEFENDED ASSET SWARM SIMULATION"
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
        "drone_body": make_material("matte carbon composite", (0.025, 0.028, 0.028, 1)),
        "friendly": make_material("friendly identification light", (0.02, 0.45, 0.95, 1)),
        "hostile_ground": make_material("hostile ground threat light", (0.95, 0.04, 0.15, 1)),
        "hostile_air": make_material("hostile air threat light", (1.0, 0.52, 0.04, 1)),
        "disabled": make_material("disabled drone marker smoke", (0.42, 0.42, 0.38, 0.35)),
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
        accent_material = materials[sample["role"]]
        obj, children = add_drone(sample, accent_material, materials["drone_body"])
        keyframe_drone(obj, children, samples[sample["id"]])

    add_neutralization_markers(samples, materials["disabled"])

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
