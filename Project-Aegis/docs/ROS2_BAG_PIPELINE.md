# ROS 2 Bag Pipeline

## Goal

Convert Aegis simulation telemetry into a ROS 2 playback artifact so the same
scenario can be reviewed in RViz, replayed through ROS tooling, or consumed by
Isaac Sim and Unreal Engine integration bridges.

## Current Export

Generate JSONL telemetry:

```bash
python3 -m aegis.cli --runs 1 --seed 42 --trace-jsonl reports/trace-42.jsonl
python3 -m aegis.cli --runs 1 --seed 42 --scenario-config scenarios/baseline_asset_defense.json --trace-jsonl reports/baseline-scenario-trace.jsonl
```

Each line contains:

- Scenario seed.
- Frame index.
- Simulation time.
- Mission metrics.
- Entity samples with SI-position and velocity fields.

## Proposed ROS 2 Messages

Initial custom interface package: `integrations/ros2/aegis_msgs`.

```text
aegis_msgs/msg/EntityState.msg
string id
string kind
string role
bool alive
float64 x_m
float64 y_m
float64 z_m
float64 vx_mps
float64 vy_mps
float64 vz_mps
```

```text
aegis_msgs/msg/EntityStateArray.msg
std_msgs/Header header
EntityState[] entities
```

```text
aegis_msgs/msg/MissionMetrics.msg
std_msgs/Header header
uint32 assets_alive
uint32 hostiles_alive
uint32 friendlies_alive
float64 attendance_rate
```

## Bridge Node Design

Package: `integrations/ros2/aegis_ros_bridge`

Node: `telemetry_replay_node`

Inputs:

- `trace_path`: JSONL telemetry path.
- `rate_hz`: replay rate.
- `loop`: whether to repeat the trace.

Outputs:

- `/clock`
- `/tf`
- `/aegis/entities`
- `/aegis/metrics`

## Workspace Build

From a ROS 2 environment:

```bash
mkdir -p ros2_ws/src
cp -r integrations/ros2/aegis_msgs ros2_ws/src/
cp -r integrations/ros2/aegis_ros_bridge ros2_ws/src/
cd ros2_ws
colcon build
source install/setup.bash
```

Replay generated telemetry:

```bash
ros2 run aegis_ros_bridge telemetry_replay_node --ros-args \
  -p trace_path:=/absolute/path/to/reports/trace-42.jsonl \
  -p rate_hz:=20.0
```

## Recording Command

```bash
ros2 bag record /clock /tf /aegis/entities /aegis/metrics -o reports/bags/trace-42
```

## Playback Command

```bash
ros2 bag play reports/bags/trace-42 --clock
```

## Implementation Notes

- Use simulation time, not wall-clock time, as the authoritative timestamp.
- Map `x_m`, `y_m`, and `z_m` directly into ENU coordinates for the first
  prototype.
- Publish a transform for each entity under frame IDs such as
  `aegis/F1/base_link`.
- Keep bag generation separate from policy execution so recorded scenarios are
  reproducible and auditable.
