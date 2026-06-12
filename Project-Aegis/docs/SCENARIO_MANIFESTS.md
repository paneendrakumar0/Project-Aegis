# Scenario Manifests

## Purpose

Scenario manifests make Aegis runs reproducible beyond random seeds. A named
mission can be reviewed, exported as telemetry, replayed into ROS 2, and
rendered in Isaac Sim or Unreal Engine with the same initial state.

## Current Format

The current manifest format is JSON with `schema_version: 1`.

Example:

```bash
python3 -m aegis.cli \
  --runs 1 \
  --seed 42 \
  --scenario-config scenarios/baseline_asset_defense.json \
  --trace-jsonl reports/baseline-scenario-trace.jsonl
```

## Coordinate Contract

- `position_m`: horizontal simulation position in meters, `[x, y]`.
- `altitude_m`: vertical position in meters.
- `velocity_mps`: horizontal velocity in meters per second, `[vx, vy]`.
- `vertical_velocity_mps`: vertical velocity in meters per second.

The current policy still reasons on the horizontal plane. The telemetry
contract is already 3D so ROS, Isaac Sim, and Unreal integrations do not need a
breaking change when full 3D maneuvering is added.

## Required Sections

- `schema_version`
- `bounds_m`
- `dt_s`
- `max_time_s`
- `intercept_radius_m`
- `assets`
- `drones`

At least one protected asset, one friendly drone, and one hostile drone are
required.

## Next Schema Additions

- Drone class definitions.
- Sensor model definitions.
- Communication degradation profiles.
- Weather and visibility.
- Multi-asset mission objectives.
- Adversary behaviour profiles.
