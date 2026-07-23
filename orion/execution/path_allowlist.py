from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Iterable


class PathPolicyError(ValueError):
    pass


class PathAllowlist:
    BLOCKED_PARTS = {
        ".git", ".env", "secrets", "credentials", "alembic", "migrations",
        "auth", "security", "__pycache__",
    }
    BLOCKED_NAMES = {"dockerfile", "railway.toml", "procfile"}

    def validate(self, paths: Iterable[str]) -> list[str]:
        validated: list[str] = []
        for raw in paths:
            normalized = str(PurePosixPath(str(raw).replace("\\", "/")))
            pure = PurePosixPath(normalized)
            if pure.is_absolute() or ".." in pure.parts:
                raise PathPolicyError(f"path_traversal_forbidden:{raw}")
            lower_parts = {part.lower() for part in pure.parts}
            if lower_parts & self.BLOCKED_PARTS:
                raise PathPolicyError(f"blocked_path:{raw}")
            if pure.name.lower() in self.BLOCKED_NAMES:
                raise PathPolicyError(f"blocked_file:{raw}")
            validated.append(normalized)
        return validated

    def resolve_inside(self, root: Path, relative: str) -> Path:
        [normalized] = self.validate([relative])
        candidate = (root / normalized).resolve()
        candidate.relative_to(root.resolve())
        return candidate
