"""
Node definitions for workflow computation units.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from typing_extensions import TypeAlias

# Type aliases for clarity
NodeId: TypeAlias = str
NodeFunction: TypeAlias = Callable[..., dict[str, Any]]


class NodeExecutor(Protocol):
    """Protocol for node execution functions."""

    def __call__(self, inputs: dict[str, Any], **context: Any) -> dict[str, Any]:
        """Execute node logic with given inputs and context."""
        ...


@dataclass
class NodeConfig:
    """Configuration for node execution."""

    timeout: float | None = None
    retry_count: int = 0
    retry_delay: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class Node:
    """Abstract base class for all workflow nodes."""

    def __init__(
        self,
        node_id: NodeId,
        executor: NodeExecutor,
        config: NodeConfig | None = None,
    ):
        self.node_id = node_id
        self.executor = executor
        self.config = config or NodeConfig()
        self._validate()

    def _validate(self) -> None:
        """Validate node configuration."""
        if not self.node_id:
            raise ValueError("Node ID cannot be empty")
        if not callable(self.executor):
            raise ValueError("Executor must be callable")

    async def execute_async(
        self, inputs: dict[str, Any], **context: Any
    ) -> dict[str, Any]:
        """Execute node asynchronously, handling both async and sync executors."""
        try:
            if asyncio.iscoroutinefunction(self.executor):
                return await self.executor(inputs, **context)
            else:
                return await asyncio.to_thread(self.executor, inputs, **context)
        except Exception as e:
            raise NodeExecutionError(
                f"Node {self.node_id} execution failed: {str(e)}"
            ) from e

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.node_id}')"


class NodeExecutionError(Exception):
    """Raised when node execution fails."""

    pass


# Convenience functions for creating common node types
def create_function_node(
    node_id: NodeId,
    func: Callable[..., dict[str, Any]],
    config: NodeConfig | None = None,
) -> Node:
    """Create a node from a Python function (sync or async)."""
    return Node(node_id=node_id, executor=func, config=config)
