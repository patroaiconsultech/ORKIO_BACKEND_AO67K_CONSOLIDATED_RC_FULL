from __future__ import annotations
import json, os
from pathlib import Path
from .base import ArtifactEnvelope

class ArtifactStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _path(self, artifact_id: str) -> Path:
        if not artifact_id.replace("_","").isalnum():
            raise ValueError("invalid_artifact_id")
        return self.root / f"{artifact_id}.json"

    def save(self, envelope: ArtifactEnvelope) -> None:
        path = self._path(envelope.artifact_id)
        self.root.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError("artifact_overwrite_forbidden")
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(envelope.to_dict(), ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(temp, path)

    def get(self, artifact_id: str) -> ArtifactEnvelope:
        return ArtifactEnvelope.from_dict(json.loads(self._path(artifact_id).read_text(encoding="utf-8")))

    def exists(self, artifact_id: str) -> bool:
        return self._path(artifact_id).exists()
