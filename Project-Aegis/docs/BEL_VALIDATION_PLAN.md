# BEL-Grade Validation Plan

## Position

Project Aegis is not ready to be shown as a finished military-grade product.
The current repository is a foundation: scenario manifests, telemetry, metrics,
Gazebo export, ROS 2 bridge scaffolding, and an interim Blender render.

To credibly present it for the BEL problem statement, the next work must focus
on mathematical validation and robotics-grade playback, not only visuals.

## Required Simulation Upgrades

### 1. 3D Vehicle Dynamics

- Position, velocity, acceleration, attitude, and angular-rate state.
- Bounded acceleration, turn rate, climb rate, and sensor field of view.
- Fixed-step deterministic integration.
- Vehicle-class envelopes for friendly and hostile drone types.

### 2. Sensor And Classification Model

- Detection range.
- Field of view.
- Latency.
- False positives and false negatives.
- Classification confidence.
- Track-loss and reacquisition behavior.

### 3. Communication-Degraded Operation

- Communication-denied baseline.
- Intermittent communication.
- Delayed message arrival.
- Local-only decision fallback.
- Optional cooperative task allocation when communication is available.

### 4. Threat And Attendance Logic

- Ground-attack hostile prioritization.
- Time-to-asset estimation.
- Intercept feasibility estimate.
- Attendance score for every urgent hostile.
- Explicit reporting of unattended threats.

### 5. Scenario Suite

At minimum:

- Balanced swarm.
- Hostile saturation.
- Multi-axis attack.
- Decoy-heavy attack.
- Multi-asset defense.
- Reduced sensor range.
- Classification uncertainty.
- Communication-denied run.
- Friendly attrition.

### 6. Statistical Evidence

Each scenario class should run hundreds or thousands of seeded trials and
produce:

- Asset survival rate.
- Hostile neutralization rate.
- Unattended threat rate.
- Friendly survival rate.
- Time-to-neutralization distribution.
- Scenario failure examples.

## Required Visualization Upgrades

### Engineering Playback

- ROS 2 bridge publishes `/clock`, `/tf`, `/aegis/entities`, and metrics.
- `rosbag2` recording is generated from reproducible scenario telemetry.
- Gazebo or RViz playback shows actual time-synchronized entity movement.

### Stakeholder Rendering

- Blender remains interim.
- Isaac Sim should be used for robotics-grade sensor/render playback.
- Unreal Engine should be used for final cinematic presentation.
- Final video must include scenario seed, commit hash, and metric summary.

## What Not To Claim Yet

- Do not claim real-world deployment readiness.
- Do not claim mathematically flawless performance.
- Do not claim sensor-fusion realism until sensor uncertainty is implemented.
- Do not claim weapon integration.

## Immediate Next Milestone

Build ROS/Gazebo playback from telemetry:

1. Build `integrations/ros2/aegis_msgs` and `aegis_ros_bridge` with `colcon`.
2. Publish entity state arrays from telemetry.
3. Add `/tf` transforms for every asset and drone.
4. Record the first `rosbag2` artifact.
5. Document replay commands and screenshots.
