from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1000
HEIGHT = 700
SCALE = 0.72
PADDING = 28
OUT_W = int(WIDTH * SCALE)
OUT_H = int(HEIGHT * SCALE)

COLORS = {
    "bg": (14, 20, 26),
    "grid": (38, 50, 60),
    "text": (238, 244, 249),
    "muted": (154, 174, 190),
    "asset": (110, 231, 168),
    "friendly": (76, 201, 240),
    "hostile_ground": (255, 92, 122),
    "hostile_air": (255, 184, 77),
    "line": (120, 170, 190),
}


def load_frames(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def xy(sample: dict) -> tuple[int, int]:
    return int(sample["x_m"] * SCALE), int(sample["y_m"] * SCALE)


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, OUT_W, 48):
        draw.line((x, 0, x, OUT_H), fill=COLORS["grid"], width=1)
    for y in range(0, OUT_H, 48):
        draw.line((0, y, OUT_W, y), fill=COLORS["grid"], width=1)


def draw_label(draw: ImageDraw.ImageDraw, text: str, pos: tuple[int, int], fill: tuple[int, int, int]) -> None:
    x, y = pos
    draw.text((x + 8, y - 8), text, fill=fill, font=font(11))


def draw_frame(frame: dict, title: str) -> Image.Image:
    image = Image.new("RGB", (OUT_W, OUT_H), COLORS["bg"])
    draw = ImageDraw.Draw(image, "RGBA")
    draw_grid(draw)

    entities = frame["entities"]
    assets = [item for item in entities if item["kind"] == "asset"]
    friendlies = [item for item in entities if item["role"] == "friendly"]
    hostiles = [item for item in entities if item["role"].startswith("hostile")]

    for asset in assets:
        x, y = xy(asset)
        draw.ellipse((x - 85, y - 85, x + 85, y + 85), outline=(*COLORS["asset"], 70), width=2)
        draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=COLORS["asset"])
        draw_label(draw, asset["id"], (x, y), COLORS["asset"])

    for hostile in hostiles:
        if not hostile["alive"]:
            continue
        x, y = xy(hostile)
        color = COLORS["hostile_ground"] if hostile["role"] == "hostile_ground" else COLORS["hostile_air"]
        radius = 7 if hostile["role"] == "hostile_air" else 8
        if hostile["role"] == "hostile_ground":
            threat_radius = max(80, int((abs(hostile["vx_mps"]) + abs(hostile["vy_mps"])) * 3.0))
            draw.ellipse((x - threat_radius, y - threat_radius, x + threat_radius, y + threat_radius), outline=(*color, 30), width=1)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
        draw_label(draw, hostile["id"], (x, y), color)

    live_hostiles = [item for item in hostiles if item["alive"]]
    for friendly in friendlies:
        if not friendly["alive"]:
            continue
        fx, fy = xy(friendly)
        if live_hostiles:
            target = min(live_hostiles, key=lambda item: (item["x_m"] - friendly["x_m"]) ** 2 + (item["y_m"] - friendly["y_m"]) ** 2)
            tx, ty = xy(target)
            draw.line((fx, fy, tx, ty), fill=(*COLORS["line"], 75), width=1)
        draw.polygon([(fx + 9, fy), (fx - 8, fy - 7), (fx - 8, fy + 7)], fill=COLORS["friendly"])
        draw_label(draw, friendly["id"], (fx, fy), COLORS["friendly"])

    banner_h = 54
    draw.rectangle((0, 0, OUT_W, banner_h), fill=(10, 15, 20, 220))
    draw.text((PADDING, 10), title, fill=COLORS["text"], font=font(18))
    metrics = (
        f"t={frame['time_s']:.1f}s  assets={frame['assets_alive']}  "
        f"friendlies={frame['friendlies_alive']}  hostiles={frame['hostiles_alive']}  "
        f"attendance={frame['attendance_rate'] * 100:.0f}%"
    )
    draw.text((PADDING, 33), metrics, fill=COLORS["muted"], font=font(12))
    return image


def draw_architecture(path: Path) -> None:
    image = Image.new("RGB", (1200, 620), COLORS["bg"])
    draw = ImageDraw.Draw(image, "RGBA")
    draw_grid(draw)

    boxes = [
        ("Scenario Manifest", 70, 245, 250, 90, COLORS["asset"]),
        ("Deterministic Core", 365, 245, 250, 90, COLORS["friendly"]),
        ("Telemetry JSONL", 660, 130, 230, 80, COLORS["hostile_air"]),
        ("Metrics CSV", 660, 360, 230, 80, COLORS["hostile_air"]),
        ("ROS 2 Bag", 950, 130, 190, 80, COLORS["hostile_ground"]),
        ("Isaac / Unreal", 950, 360, 190, 80, COLORS["hostile_ground"]),
    ]
    for text, x, y, w, h, color in boxes:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=8, outline=color, width=3, fill=(24, 33, 42, 235))
        draw.text((x + 18, y + 30), text, fill=COLORS["text"], font=font(22))

    arrows = [
        ((320, 290), (365, 290)),
        ((615, 280), (660, 170)),
        ((615, 305), (660, 400)),
        ((890, 170), (950, 170)),
        ((890, 400), (950, 400)),
    ]
    for start, end in arrows:
        draw.line((*start, *end), fill=COLORS["line"], width=4)
        ex, ey = end
        draw.polygon([(ex, ey), (ex - 12, ey - 7), (ex - 12, ey + 7)], fill=COLORS["line"])

    draw.text((58, 52), "Project Aegis Industrial Simulation Pipeline", fill=COLORS["text"], font=font(32))
    draw.text((60, 95), "One scenario seed drives metrics, ROS bag playback, and cinematic rendering.", fill=COLORS["muted"], font=font(18))
    image.save(path)


def write_mp4(frames: list[dict], path: Path, fps: int = 8) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        frame_dir = Path(temp_dir)
        for index, frame in enumerate(frames):
            image = draw_frame(frame, "Project Aegis Mission Recording")
            image.save(frame_dir / f"frame_{index:04d}.png")

        command = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frame_dir / "frame_%04d.png"),
            "-vf",
            "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_demo_manifest(path: Path, trace_path: Path, out_dir: Path, frame_count: int) -> None:
    manifest = {
        "schema_version": 1,
        "scenario": "scenarios/baseline_asset_defense.json",
        "trace": str(trace_path),
        "frame_count": frame_count,
        "media": {
            "pipeline_png": str(out_dir / "simulation-pipeline.png"),
            "snapshot_png": str(out_dir / "mission-snapshot.png"),
            "replay_gif": str(out_dir / "mission-replay.gif"),
            "recording_mp4": str(out_dir / "mission-recording.mp4"),
        },
        "commands": {
            "trace": "make scenario-trace",
            "media": "make media",
            "tests": "make test",
        },
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Project Aegis README media from telemetry.")
    parser.add_argument("--trace", default="reports/baseline-scenario-trace.jsonl")
    parser.add_argument("--out-dir", default="assets/media")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = load_frames(Path(args.trace))
    if not frames:
        raise SystemExit("trace has no frames")

    selected_indexes = sorted(set([0, len(frames) // 3, (2 * len(frames)) // 3, len(frames) - 1]))
    gif_frames = [draw_frame(frames[index], "Project Aegis Mission Replay") for index in selected_indexes]
    gif_frames[0].save(
        out_dir / "mission-replay.gif",
        save_all=True,
        append_images=gif_frames[1:],
        duration=600,
        loop=0,
    )
    draw_frame(frames[len(frames) // 2], "Project Aegis Tactical Snapshot").save(out_dir / "mission-snapshot.png")
    draw_architecture(out_dir / "simulation-pipeline.png")
    try:
        write_mp4(frames, out_dir / "mission-recording.mp4")
    except FileNotFoundError:
        print("ffmpeg not found, skipping mission-recording.mp4 generation.")
    write_demo_manifest(out_dir / "demo-manifest.json", Path(args.trace), out_dir, len(frames))
    print(f"wrote media to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
