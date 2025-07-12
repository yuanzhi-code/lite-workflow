"""
High-level workflow interface for easy usage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..core.error_handler import ErrorHandler
from ..core.state_manager import StateManager
from ..definitions.edge import Edge
from ..definitions.graph import Graph
from ..definitions.node import Node, create_function_node
from ..definitions.state import InMemoryState, State
from .pregel_engine import PregelEngine


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    final_state: State
    execution_stats: dict[str, Any]
    success: bool
    error: str | None = None


class Workflow:
    """High-level workflow interface."""

    def __init__(
        self,
        name: str,
        initial_state: dict[str, Any] | None = None,
    ):
        self.name = name
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self.initial_state = initial_state or {}
        self._start_node: str | None = None

    def add_node(
        self, node_id: str, func: Callable[..., dict[str, Any]], **kwargs: Any
    ) -> Workflow:
        """Add a function node to the workflow."""
        node = create_function_node(node_id, func)
        self.nodes.append(node)

        if not self._start_node:
            self._start_node = node_id

        return self

    def add_edge(self, source: str, target: str, **kwargs: Any) -> Workflow:
        """Add an edge between nodes."""
        edge = Edge(source_id=source, target_id=target, **kwargs)
        self.edges.append(edge)
        return self

    def set_start_node(self, node_id: str) -> Workflow:
        """Set the start node for the workflow."""
        self._start_node = node_id
        return self

    def chain(self, *nodes: str) -> Workflow:
        """Create a linear chain of nodes."""
        for i in range(len(nodes) - 1):
            self.add_edge(nodes[i], nodes[i + 1])
        return self

    def build_graph(self) -> Graph:
        """Build the graph from current workflow definition."""
        if not self._start_node:
            raise ValueError("Start node must be set")

        return Graph(
            graph_id=self.name,
            nodes=self.nodes,
            edges=self.edges,
            start_node=self._start_node,
        )

    def run(self, **kwargs: Any) -> WorkflowResult:
        """Run the workflow."""
        try:
            graph = self.build_graph()

            state_manager = StateManager(self.initial_state)
            error_handler = ErrorHandler()

            engine = PregelEngine(graph, state_manager, error_handler, **kwargs)

            final_state = engine.execute()
            stats = engine.get_execution_stats()

            return WorkflowResult(
                final_state=final_state, execution_stats=stats, success=True
            )

        except Exception as e:
            return WorkflowResult(
                final_state=InMemoryState({}),
                execution_stats={},
                success=False,
                error=str(e),
            )

    def __repr__(self) -> str:
        return f"Workflow(name='{self.name}', nodes={len(self.nodes)}, edges={len(self.edges)})"
