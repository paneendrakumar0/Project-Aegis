import json
from pathlib import Path


def test_demo_manifest_media_files_exist() -> None:
    manifest_path = Path("assets/media/demo-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    assert manifest["frame_count"] > 0
    for media_path in manifest["media"].values():
        assert Path(media_path).exists()
