# Workstation Setup

## Detected Local Environment

- Ubuntu 22.04.5 LTS.
- ROS 2 Humble available at `/opt/ros/humble`.
- `colcon` is installed.
- Gazebo Classic 11.10.2 is installed.
- Gazebo Sim / Ignition libraries and ROS-Gazebo bridge packages are present.
- NVIDIA RTX 4060 Laptop GPU detected.
- NVIDIA driver 580.126.09 and CUDA 13.0 reported by `nvidia-smi`.
- `ffmpeg` is installed.

## Recommended Install Order

### 1. Use What Is Already Installed

The next engineering target should use the existing stack:

- ROS 2 Humble.
- Gazebo Classic / Gazebo Sim libraries.
- `rosbag2`.
- `ffmpeg`.

This is enough to build trajectory playback, ROS bag generation, and an
engineering simulator demo.

### 2. Add Blender For Interim Cinematic Renders

Install Blender before Unreal or Isaac Sim if a quick high-quality offline
render is needed. It is lighter, scriptable from Python, and useful for
producing polished mission videos from telemetry while the robotics simulator
work matures.

Suggested package:

```bash
sudo apt install blender
```

Blender is now installed on this workstation and `make blender-render` is the
current local cinematic-render command.

### 3. Add Isaac Sim For Robotics-Grade Sensor Simulation

Install Isaac Sim when the project needs:

- Camera, LiDAR, radar-like, or synthetic perception rendering.
- USD assets and robotics-grade scene playback.
- NVIDIA RTX rendering.
- ROS 2 bridge workflows.

This should come after the telemetry and ROS playback path is stable.

### 4. Add Unreal Engine For Final Presentation Video

Install Unreal Engine when the project needs a cinematic stakeholder video with
Sequencer, camera choreography, high-quality environments, and Movie Render
Queue output.

Unreal is not required to validate the algorithm. It is for final presentation
quality.

## Immediate Next Build Target

Build a ROS/Gazebo playback path:

1. Generate Aegis telemetry.
2. Export a Gazebo world and trajectory CSV.
3. Build the ROS 2 bridge packages with `colcon`.
4. Publish entity states over ROS 2.
5. Record `/clock`, `/aegis/entities`, `/aegis/metrics`, and transforms into
   `rosbag2`.
6. Use Gazebo/RViz for engineering review.
