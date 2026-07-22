from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path


@dataclass(frozen=True)
class ReleaseIdentity:
    release_id: str
    commit_sha: str
    deployment_id: str
    main_sha256: str


def _first_env(*names: str, default: str = "unknown") -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return default


def build_release_identity(main_file: str) -> ReleaseIdentity:
    path = Path(main_file)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return ReleaseIdentity(
        release_id=_first_env(
            "RELEASE_ID",
            "RAILWAY_DEPLOYMENT_ID",
            "DEPLOYMENT_ID",
        ),
        commit_sha=_first_env(
            "RAILWAY_GIT_COMMIT_SHA",
            "GIT_COMMIT_SHA",
            "COMMIT_SHA",
        ),
        deployment_id=_first_env(
            "RAILWAY_DEPLOYMENT_ID",
            "DEPLOYMENT_ID",
        ),
        main_sha256=digest,
    )
