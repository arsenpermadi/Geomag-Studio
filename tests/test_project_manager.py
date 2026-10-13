import json
from pathlib import Path

import pytest

from geomag_studio.project_manager import ProjectError, ProjectManager


def test_create_project_builds_structure_and_manifest(tmp_path: Path) -> None:
    project = ProjectManager.create(tmp_path / "survey", "Survey A", {"authority": "EPSG", "code": 4326})

    assert project.manifest_path.is_file()
    assert project.manifest["name"] == "Survey A"
    assert project.manifest["coordinate_reference_system"]["code"] == 4326
    assert (project.root / "data" / "raw" / "seaspy2").is_dir()
    assert (project.root / "data" / "raw" / "geometrics_g852").is_dir()


def test_project_can_be_reopened_after_save(tmp_path: Path) -> None:
    project = ProjectManager.create(tmp_path / "survey", "Survey A")
    project.add_dataset({"dataset_id": "dataset-1", "name": "Imported data"})
    project.save()

    reopened = ProjectManager.open(project.root)

    assert reopened.manifest["project_id"] == project.manifest["project_id"]
    assert reopened.manifest["datasets"][0]["dataset_id"] == "dataset-1"


def test_open_rejects_invalid_manifest(tmp_path: Path) -> None:
    root = tmp_path / "broken"
    root.mkdir()
    (root / "project.json").write_text(json.dumps({"name": "broken"}), encoding="utf-8")

    with pytest.raises(ProjectError, match="missing keys"):
        ProjectManager.open(root)


def test_project_rejects_non_empty_directory(tmp_path: Path) -> None:
    root = tmp_path / "existing"
    root.mkdir()
    (root / "notes.txt").write_text("existing", encoding="utf-8")

    with pytest.raises(ProjectError, match="not empty"):
        ProjectManager.create(root, "Survey A")

