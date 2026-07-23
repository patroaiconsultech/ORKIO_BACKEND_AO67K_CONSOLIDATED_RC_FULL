from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


class WorkspaceManager:
    def create(self, source_repo: str | Path) -> Path:
        source = Path(source_repo).resolve()
        if not source.is_dir():
            raise FileNotFoundError(f"repository_not_found:{source}")
        root = Path(tempfile.mkdtemp(prefix="orion_workspace_"))
        target = root / "repo"
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".env", ".env.*"),
        )
        return target

    def cleanup(self, workspace: str | Path) -> None:
        path = Path(workspace).resolve()
        if not path.name == "repo" or not path.parent.name.startswith("orion_workspace_"):
            raise ValueError("unsafe_workspace_cleanup_path")
        shutil.rmtree(path.parent, ignore_errors=False)
