from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

from orion.contracts.models import PatchArtifact


class DiffGenerator:
    def generate_for_file(
        self,
        *,
        repo_root: str | Path,
        relative_path: str,
        new_content: str,
        proposal_id: str,
    ) -> PatchArtifact:
        root = Path(repo_root).resolve()
        path = (root / relative_path).resolve()
        path.relative_to(root)
        old_content = path.read_text(encoding="utf-8")
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = "".join(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{relative_path}",
            tofile=f"b/{relative_path}",
        ))
        return PatchArtifact(
            proposal_id=proposal_id,
            unified_diff=diff,
            files_changed=[relative_path],
            before_hashes={relative_path: hashlib.sha256(old_content.encode()).hexdigest()},
            expected_after_hashes={relative_path: hashlib.sha256(new_content.encode()).hexdigest()},
        )
