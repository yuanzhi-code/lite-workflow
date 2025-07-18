"""
Graph definitions for workflow structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (  # Keep original types for compatibility with py38 target, ruff might be overly aggressive
    Any,
)

from typing_extensions import TypeAlias

from .edge import Edge
from .node import Node, NodeId

# Type aliases
GraphId: TypeAlias = str


@dataclass
class GraphConfig:
    """Configuration for graph execution."""

    max_iterations: int = 1000
    enable_parallel: bool = True
    timeout: float | None = None  # UP045
    metadata: dict[str, Any] = field(default_factory=dict)  # UP006


class Graph:
    """A directed graph representing a workflow."""

    def __init__(
        self,
        graph_id: GraphId,
        nodes: list[Node],  # UP006
        edges: list[Edge],  # UP006
        start_node: NodeId,
        end_nodes: set[NodeId] | None = None,  # UP045, UP006
        config: GraphConfig | None = None,  # UP045
    ):
        self.graph_id = graph_id
        self.nodes = {node.node_id: node for node in nodes}
        self.edges = edges
        self.start_node = start_node
        self.end_nodes = end_nodes or set()
        self.config = config or GraphConfig()

        self._validate()
        self._build_adjacency_lists()

    def _validate(self) -> None:
        """Validate graph structure."""
        if not self.graph_id:
            raise ValueError("Graph ID cannot be empty")

        if self.start_node not in self.nodes:
            raise ValueError(f"Start node '{self.start_node}' not found")

        for edge in self.edges:
            if edge.source_id not in self.nodes:
                raise ValueError(f"Source node '{edge.source_id}' not found")
            if edge.target_id not in self.nodes:
                raise ValueError(f"Target node '{edge.target_id}' not found")

    def _build_adjacency_lists(self) -> None:
        """Build adjacency lists for efficient traversal."""
        self._out_edges: dict[NodeId, list[Edge]] = {
            node_id: [] for node_id in self.nodes
        }  # UP006
        self._in_edges: dict[NodeId, list[Edge]] = {
            node_id: [] for node_id in self.nodes
        }  # UP006

        for edge in self.edges:
            self._out_edges[edge.source_id].append(edge)
            self._in_edges[edge.target_id].append(edge)

    def get_node(self, node_id: NodeId) -> Node | None:  # UP045
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_outgoing_edges(self, node_id: NodeId) -> list[Edge]:  # UP006
        """Get all outgoing edges from a node."""
        return self._out_edges.get(node_id, [])

    def get_incoming_edges(self, node_id: NodeId) -> list[Edge]:  # UP006
        """Get all incoming edges to a node."""
        return self._in_edges.get(node_id, [])

    def get_successors(self, node_id: NodeId) -> list[NodeId]:  # UP006
        """Get direct successor node IDs."""
        return [edge.target_id for edge in self.get_outgoing_edges(node_id)]

    def get_predecessors(self, node_id: NodeId) -> list[NodeId]:  # UP006
        """Get direct predecessor node IDs."""
        return [edge.source_id for edge in self.get_incoming_edges(node_id)]

    def is_terminal(self, node_id: NodeId) -> bool:
        """Check if node is a terminal/end node."""
        return not self.get_outgoing_edges(node_id)

    def topological_sort(self) -> list[NodeId]:  # UP006
        """Return nodes in topological order."""
        visited = set()
        result = []

        def dfs(node_id: NodeId) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            for successor in self.get_successors(node_id):
                dfs(successor)
            result.append(node_id)

        dfs(self.start_node)
        return result

    def validate_cycles(self) -> bool:
        """Check if graph contains cycles."""
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: NodeId) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self.get_successors(node_id):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return False
        return True

    def __repr__(self) -> str:
        return (
            f"Graph(id='{self.graph_id}', "
            f"nodes={len(self.nodes)}, edges={len(self.edges)})"
        )

    def __len__(self) -> int:
        """Return number of nodes in graph."""
        return len(self.nodes)
