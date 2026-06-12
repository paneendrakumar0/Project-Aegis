# Media Assets

## Purpose

README media is generated from Project Aegis telemetry so visual artifacts stay
aligned with the simulation, scenario manifest, and metrics.

## Generate Media

```bash
make media
```

This command runs the baseline scenario manifest, writes a JSONL trace, and
renders:

- `assets/media/simulation-pipeline.png`
- `assets/media/mission-snapshot.png`
- `assets/media/mission-replay.gif`
- `assets/media/mission-recording.mp4`
- `assets/media/demo-manifest.json`
- `assets/blender/aegis_blender_snapshot.png`
- `assets/blender/aegis_blender_mission.mp4`

## Source Of Truth

Current media source:

```text
scenarios/baseline_asset_defense.json
reports/baseline-scenario-trace.jsonl
tools/render_trace_media.py
```

The GIF and PNG files are committed intentionally because they are part of the
public project presentation. The MP4 is committed as a compact mission
recording for reviewers who prefer video playback. Generated CSV and JSONL
report outputs remain ignored unless a release package needs to include them.

Blender outputs are committed separately under `assets/blender/` because they
are the stronger interim visual artifacts for stakeholder review.
