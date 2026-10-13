"""Creation and persistence of GeoMag Studio projects.

This module intentionally uses only the Python standard library. It is the
first persistence layer and can later be used by the desktop UI and services.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping
from uuid import uuid4


SCHEMA_VERSION = "1.0"
APPLICATION_VERSION = "0.1.0"


class ProjectError(ValueError):
    """Raised when a project cannot be created, opened, or saved."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ProjectManager:
    """Manage a directory-based GeoMag Studio project."""

    REQUIRED_MANIFEST_KEYS = {
        "schema_version",
        "project_id",
        "name",
        "created_at",
        "updated_at",
        "application",
        "datasets",
        "workflow",
        "layers",
        "provenance",
    }

    PROJECT_DIRECTORIES = (
        "metadata",
        "data/raw/seaspy2",
        "data/raw/geometrics_g852",
        "data/imported",
        "data/corrected",
        "data/processed",
        "data/grids",
        "workflow",
        "interpretation/picks",
        "interpretation/models",
        "interpretation/constraints",
        "layouts",
        "exports",
        "reports",
    )

    def __init__(self, root: Path, manifest: dict[str, Any]) -> None:
        self.root = root.resolve()
        self.manifest = manifest

    @classmethod
    def create(
        cls,
        root: str | Path,
        name: str,
        crs: Mapping[str, Any] | None = None,
    ) -> "ProjectManager":
        """Create a new project directory and its initial manifest."""
        project_root = Path(root).expanduser().resolve()
        if project_root.exists() and any(project_root.iterdir()):
            raise ProjectError(f"Project directory is not empty: {project_root}")

        if not name.strip():
            raise ProjectError("Project name cannot be empty")

        project_root.mkdir(parents=True, exist_ok=True)
        for directory in cls.PROJECT_DIRECTORIES:
            (project_root / directory).mkdir(parents=True, exist_ok=True)

        now = _utc_now()
        manifest: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "project_id": str(uuid4()),
            "name": name.strip(),
            "created_at": now,
            "updated_at": now,
            "application": {
                "name": "GeoMag Studio",
                "version": APPLICATION_VERSION,
            },
            "coordinate_reference_system": crs,
            "datasets": [],
            "workflow": {
                "pipeline_file": "workflow/pipeline.json",
                "last_completed_operation_id": None,
            },
            "layers": [],
            "provenance": {
                "history_file": "metadata/processing_history.json",
            },
        }
        manager = cls(project_root, manifest)
        manager.save()
        return manager

    @classmethod
    def open(cls, root: str | Path) -> "ProjectManager":
        """Open and validate an existing project."""
        project_root = Path(root).expanduser().resolve()
        manifest_path = project_root / "project.json"
        if not manifest_path.is_file():
            raise ProjectError(f"Manifest not found: {manifest_path}")

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ProjectError(f"Invalid project.json: {exc}") from exc

        cls._validate_manifest(manifest)
        return cls(project_root, manifest)

    @property
    def manifest_path(self) -> Path:
        return self.root / "project.json"

    def save(self) -> None:
        """Persist the manifest using a temporary file and atomic replacement."""
        self._validate_manifest(self.manifest)
        self.manifest["updated_at"] = _utc_now()
        self.root.mkdir(parents=True, exist_ok=True)

        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.root,
                prefix="project.",
                suffix=".json.tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                json.dump(self.manifest, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            temporary_path.replace(self.manifest_path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def add_dataset(self, dataset: Mapping[str, Any]) -> None:
        """Register a dataset after checking its stable identifier."""
        item = dict(dataset)
        dataset_id = item.get("dataset_id")
        if not dataset_id:
            raise ProjectError("Dataset must have a dataset_id")
        if any(existing.get("dataset_id") == dataset_id for existing in self.manifest["datasets"]):
            raise ProjectError(f"Dataset ID already exists: {dataset_id}")
        self.manifest["datasets"].append(item)

    def relative_path(self, path: str | Path) -> str:
        """Return a project-relative path, or a normalized external path."""
        candidate = Path(path).expanduser().resolve()
        try:
            return candidate.relative_to(self.root).as_posix()
        except ValueError:
            return candidate.as_posix()

    @classmethod
    def _validate_manifest(cls, manifest: Any) -> None:
        if not isinstance(manifest, dict):
            raise ProjectError("Project manifest must be a JSON object")
        missing = cls.REQUIRED_MANIFEST_KEYS - manifest.keys()
        if missing:
            raise ProjectError(f"Manifest is missing keys: {', '.join(sorted(missing))}")
        if manifest["schema_version"] != SCHEMA_VERSION:
            raise ProjectError(
                f"Unsupported schema version: {manifest['schema_version']} "
                f"(expected {SCHEMA_VERSION})"
            )
        if not isinstance(manifest["datasets"], list):
            raise ProjectError("Manifest datasets must be a list")
        if not isinstance(manifest["layers"], list):
            raise ProjectError("Manifest layers must be a list")

