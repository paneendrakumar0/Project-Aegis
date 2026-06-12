from pathlib import Path


def test_blender_render_assets_exist() -> None:
    assert Path("assets/blender/aegis_blender_snapshot.png").exists()
    assert Path("assets/blender/aegis_blender_mission.mp4").exists()
