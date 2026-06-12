# Industrial Simulation Plan

## Direction

Project Aegis should mature from a lightweight research prototype into a
defense-grade simulation product with three distinct layers:

1. Authoritative simulation core: deterministic scenarios, physics state,
   policy decisions, and reproducible metrics.
2. Mission telemetry layer: frame-by-frame data that can be exported to JSONL,
   CSV, ROS 2 topics, and ROS 2 bags.
3. High-fidelity visualization layer: Isaac Sim, Unreal Engine, or both, driven
   by recorded telemetry rather than hand-animated scenes.

The browser view remains a convenience viewer only. It is not the target
product experience.

## Target Pipeline

```text
Aegis Scenario Config
        |
        v
Deterministic Simulation Core
        |
        +--> Metrics CSV / Evaluation Report
        |
        +--> Telemetry JSONL
                 |
                 +--> ROS 2 Topic Publisher
                 |        |
                 |        v
                 |    rosbag2 Recording
                 |
                 +--> Isaac Sim Playback Extension
                 |
                 +--> Unreal Engine Sequencer Import
```

## Why Telemetry First

The recorded telemetry is the single source of truth for visualization. This
keeps the algorithm, evaluation metrics, and cinematic render consistent. If a
movie-quality render is generated later, every drone movement should be traced
back to a simulation frame and seed.

## Precision Upgrades

The current baseline is intentionally simple. Industrial-grade maturity needs:

- 3D state model: position, velocity, acceleration, attitude, angular rate.
- Unit discipline: SI units for all internal state and exported telemetry.
- Fixed-step integration: deterministic replay at a configured simulation rate.
- Scenario manifests: versioned YAML/JSON scenario definitions.
- Vehicle envelopes: speed, turn-rate, acceleration, sensor, and endurance
  constraints per drone class.
- Sensor model: detection range, field of view, latency, false positives, false
  negatives, and classification confidence.
- Communication model: denied, degraded, intermittent, and available modes.
- Adversary model: direct attack, evasive attack, decoy, saturation, and split
  swarm behaviour.
- Evaluation gates: reproducibility checks, regression tests, and scenario
  suites.

## ROS 2 Bag Strategy

The recommended route is to build a ROS 2 bridge package that reads Aegis
telemetry frames and publishes:

- `/aegis/entities`: entity state array for all assets and drones.
- `/aegis/metrics`: per-frame mission metrics.
- `/tf`: transforms for each drone and asset frame.
- `/clock`: simulation time for deterministic playback.

Then record:

```bash
ros2 bag record /clock /tf /aegis/entities /aegis/metrics
```

This produces a `rosbag2` artifact that can be replayed, inspected in RViz, or
used as a source for higher-fidelity rendering tools.

## Isaac Sim Strategy

Isaac Sim is best for robotics-grade simulation and sensor realism:

- Import drone USD assets.
- Drive each drone transform from Aegis telemetry or ROS 2 topics.
- Add sensor frustums, LiDAR/radar visualizations, and tracked-object overlays.
- Render synchronized camera passes for technical demos.
- Use domain-specific scene environments for airbase, border, ship deck, or
  strategic-asset protection scenarios.

## Unreal Engine Strategy

Unreal Engine is best for cinematic output and presentation impact:

- Import Aegis telemetry as animation curves or via a live UDP/ROS bridge.
- Spawn drone actors with physically plausible materials and navigation trails.
- Use Sequencer for camera paths, labels, heatmaps, and operator HUD overlays.
- Render final video with Movie Render Queue.

## Product Standard

For BEL/DRDO-style review, the product should show:

- Repeatable scenario seed.
- Quantitative report.
- Recorded telemetry.
- ROS bag playback.
- High-fidelity rendered mission video.
- Clear explanation of assumptions and safety boundaries.
