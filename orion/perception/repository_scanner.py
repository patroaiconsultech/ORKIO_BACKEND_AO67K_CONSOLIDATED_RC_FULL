from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from orion.contracts.models import Evidence


class RepositoryScanner:
    def scan(self, repo_root: str | Path) -> list[Evidence]:
        root = Path(repo_root).resolve()
        evidence: list[Evidence] = []
        for path in sorted(root.rglob("*.py")):
            if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
                continue
            relative = path.relative_to(root).as_posix()
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            try:
                tree = ast.parse(raw.decode("utf-8"))
                imports = sum(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))
                functions = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
                fact = f"python_file imports={imports} functions={functions} bytes={len(raw)}"
                confidence = 1.0
            except (SyntaxError, UnicodeDecodeError) as exc:
                fact = f"python_parse_failure:{type(exc).__name__}"
                confidence = 1.0
            evidence.append(Evidence(
                source_type="repository",
                source_ref=relative,
                fact=fact,
                confidence=confidence,
                raw_hash=digest,
            ))
        return evidence
