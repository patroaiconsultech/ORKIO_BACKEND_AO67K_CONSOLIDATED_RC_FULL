from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_supports_package_and_legacy_import_roots() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "ENV PYTHONPATH=/:/app" in dockerfile
    assert "python /app/scripts/preflight_python_namespace.py" in dockerfile
    assert "app.main:app" in dockerfile


def test_preflight_validates_repository_and_package_parent_paths() -> None:
    source = (
        ROOT / "scripts" / "preflight_python_namespace.py"
    ).read_text(encoding="utf-8")

    assert "REPOSITORY_ROOT" in source
    assert "PACKAGE_PARENT" in source
    assert "_validate_required_paths()" in source
    assert "python_namespace_required_paths_missing" in source
