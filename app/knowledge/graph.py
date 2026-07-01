from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import uuid


@dataclass(frozen=True)
class GraphNode:
    label: str
    node_type: str
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    relation: str


class PatroAIKnowledgeGraph:
    """Starter in-memory graph for future canonical knowledge relationships."""

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, label: str, node_type: str) -> GraphNode:
        node = GraphNode(label=label, node_type=node_type)
        self.nodes[node.node_id] = node
        return node

    def connect(self, source: GraphNode, target: GraphNode, relation: str) -> GraphEdge:
        edge = GraphEdge(source_id=source.node_id, target_id=target.node_id, relation=relation)
        self.edges.append(edge)
        return edge

    def neighbors(self, node: GraphNode, relation: str | None = None) -> List[GraphNode]:
        result: List[GraphNode] = []
        for edge in self.edges:
            if edge.source_id == node.node_id and (relation is None or edge.relation == relation):
                target = self.nodes.get(edge.target_id)
                if target:
                    result.append(target)
        return result
