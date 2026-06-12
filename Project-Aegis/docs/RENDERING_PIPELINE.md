# High-Fidelity Rendering Pipeline

## Goal

Produce excellent mission videos from real simulation telemetry, not manually
animated approximations. Every rendered drone path should correspond to an
Aegis scenario seed and recorded telemetry trace.

## Recommended Tool Split

Isaac Sim:

- Robotics and sensor-oriented visualization.
- ROS 2 topic playback.
- USD asset workflow.
- Synthetic sensor overlays and technical review scenes.

Unreal Engine:

- Cinematic presentation.
- Sequencer timeline control.
- Advanced camera moves and rendered video output.
- Mission HUD overlays for stakeholder demos.

## Asset Requirements

- Friendly drone model.
- Hostile drone model variants.
- Protected asset model.
- Environment scenes: base, border sector, ship deck, or strategic facility.
- Material variants for friendly, hostile air-threat, and hostile ground-attack
  entities.
- Trail, sensor cone, and threat-ring visual effects.

## Telemetry Mapping

Use the telemetry fields:

- `x_m`, `y_m`, `z_m` for position.
- `vx_mps`, `vy_mps`, `vz_mps` for forward-vector estimation.
- `role` for material and label selection.
- `alive` for visibility, explosion marker, or neutralized-state transition.

## Movie Output Structure

Recommended shot sequence:

1. Establishing shot of protected asset and inbound swarm.
2. Tactical top-down view showing threat rings and assignments.
3. Close pass of friendly interceptors converging.
4. Split-screen or HUD shot with attendance and neutralization metrics.
5. Final summary frame with scenario seed and quantitative outcome.

## Quality Bar

- 4K render target for final export.
- Stable camera paths, no shaky default viewport capture.
- Entity labels and trails visible but not cluttered.
- Mission metrics synchronized with simulation time.
- Render metadata includes scenario seed, telemetry file, and commit hash.
