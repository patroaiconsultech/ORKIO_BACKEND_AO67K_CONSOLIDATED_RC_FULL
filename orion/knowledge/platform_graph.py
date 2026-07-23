from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class PlatformGraph:
    nodes: Set[str] = field(default_factory=set)
    edges: Set[Tuple[str, str, str]] = field(default_factory=set)

    def add_node(self, node_id: str) -> None:
        self.nodes.add(node_id)

    def add_edge(self, source: str, relation: str, target: str) -> None:
        self.nodes.update({source, target})
        self.edges.add((source, relation, target))

    @classmethod
    def from_repository(cls, repo_root: str | Path) -> "PlatformGraph":
        root = Path(repo_root).resolve()
        graph = cls()
        for path in sorted(root.rglob("*.py")):
            if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
                continue
            relative = path.relative_to(root).with_suffix("").as_posix()
            module = relative.replace("/", ".")
            source_id = f"module:{module}"
            graph.add_node(source_id)
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        graph.add_edge(source_id, "imports", f"module:{alias.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    graph.add_edge(source_id, "imports", f"module:{node.module}")
        return graph

    def dependents_of(self, target: str) -> List[str]:
        return sorted(source for source, relation, dest in self.edges
                      if relation == "imports" and dest == target)
