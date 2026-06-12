from __future__ import annotations

import json
from pathlib import Path

import rclpy
from aegis_msgs.msg import EntityState, EntityStateArray, MissionMetrics
from rclpy.node import Node
from rosgraph_msgs.msg import Clock


class TelemetryReplayNode(Node):
    def __init__(self) -> None:
        super().__init__("aegis_telemetry_replay")
        self.declare_parameter("trace_path", "reports/trace-42.jsonl")
        self.declare_parameter("rate_hz", 20.0)
        self.declare_parameter("loop", False)

        self.frames = self._load_frames(Path(self.get_parameter("trace_path").value))
        self.index = 0
        self.entities_pub = self.create_publisher(EntityStateArray, "/aegis/entities", 10)
        self.metrics_pub = self.create_publisher(MissionMetrics, "/aegis/metrics", 10)
        self.clock_pub = self.create_publisher(Clock, "/clock", 10)

        rate_hz = float(self.get_parameter("rate_hz").value)
        self.timer = self.create_timer(1.0 / max(rate_hz, 1.0), self._publish_next)
        self.get_logger().info(f"loaded {len(self.frames)} Aegis telemetry frames")

    def _load_frames(self, path: Path) -> list[dict]:
        if not path.exists():
            raise FileNotFoundError(f"trace file not found: {path}")
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _publish_next(self) -> None:
        if not self.frames:
            return
        if self.index >= len(self.frames):
            if bool(self.get_parameter("loop").value):
                self.index = 0
            else:
                return

        frame = self.frames[self.index]
        stamp = self.get_clock().now().to_msg()

        clock = Clock()
        seconds = int(frame["time_s"])
        clock.clock.sec = seconds
        clock.clock.nanosec = int((frame["time_s"] - seconds) * 1_000_000_000)
        self.clock_pub.publish(clock)

        entities = EntityStateArray()
        entities.header.stamp = stamp
        entities.header.frame_id = "aegis_world"
        for sample in frame["entities"]:
            entity = EntityState()
            entity.id = sample["id"]
            entity.kind = sample["kind"]
            entity.role = sample["role"]
            entity.alive = sample["alive"]
            entity.x_m = float(sample["x_m"])
            entity.y_m = float(sample["y_m"])
            entity.z_m = float(sample["z_m"])
            entity.vx_mps = float(sample["vx_mps"])
            entity.vy_mps = float(sample["vy_mps"])
            entity.vz_mps = float(sample["vz_mps"])
            entities.entities.append(entity)
        self.entities_pub.publish(entities)

        metrics = MissionMetrics()
        metrics.header = entities.header
        metrics.assets_alive = int(frame["assets_alive"])
        metrics.hostiles_alive = int(frame["hostiles_alive"])
        metrics.friendlies_alive = int(frame["friendlies_alive"])
        metrics.attendance_rate = float(frame["attendance_rate"])
        self.metrics_pub.publish(metrics)

        self.index += 1


def main() -> None:
    rclpy.init()
    node = TelemetryReplayNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

