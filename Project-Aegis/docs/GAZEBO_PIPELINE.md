# Gazebo Simulation Pipeline

## Purpose

Gazebo is the local robotics-simulation bridge between the Python policy core
and higher-end renderers such as Isaac Sim or Unreal Engine. It is more
appropriate for technical review than the lightweight browser canvas because it
uses robotics simulator conventions, SDF worlds, and ROS/Gazebo tooling.

## Generate Scene Artifacts

```bash
make gazebo-scene
```

This produces:

- `integrations/gazebo/worlds/aegis_baseline.world`
- `integrations/gazebo/trajectories/aegis_baseline_trajectory.csv`

The world contains the protected asset and drone models at the first telemetry
frame. The trajectory CSV preserves the full recorded path for playback bridge
work.

## Open World

Gazebo Classic 11:

```bash
gazebo integrations/gazebo/worlds/aegis_baseline.world
```

## Next Engineering Step

Add a Gazebo model-control plugin or ROS 2 node that reads
`aegis_baseline_trajectory.csv` and publishes entity poses into Gazebo over
simulation time. That will replace the static scene with synchronized playback.

## Review Positioning

For BEL/DRDO-style review, present Gazebo as the engineering simulator and
Isaac/Unreal as the cinematic renderer. The browser view should be treated as a
developer convenience only.
