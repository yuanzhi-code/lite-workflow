"""
Node definitions for workflow computation units.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Callable, Optional, Protocol
from typing_extensions import TypeAlias

# Type aliases for clarity
NodeId: TypeAlias = str
NodeFunction: TypeAlias = Callable[..., Dict[str, Any]]


class NodeExecutor(Protocol):
    """Protocol for node execution functions."""
    
    def __call__(self, inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
        """Execute node logic with given inputs and context."""
        ...


@dataclass
class NodeConfig:
    """Configuration for node execution."""
    timeout: Optional[float] = None
    retry_count: int = 0
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseNode(ABC):
    """Abstract base class for all workflow nodes."""
    
    def __init__(
        self,
        node_id: NodeId,
        executor: NodeExecutor,
        config: Optional[NodeConfig] = None
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
    
    async def execute_async(self, inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
        """Execute node asynchronously."""
        return await self._execute_with_context(inputs, **context)
    
    def execute(self, inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
        """Execute node synchronously."""
        return self._execute_with_context(inputs, **context)
    
    def _execute_with_context(self, inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
        """Execute node with proper context handling."""
        try:
            return self.executor(inputs, **context)
        except Exception as e:
            raise NodeExecutionError(
                f"Node {self.node_id} execution failed: {str(e)}"
            ) from e
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.node_id}')"


class Node(BaseNode):
    """Standard workflow node with synchronous execution."""
    pass


class AsyncNode(BaseNode):
    """Asynchronous workflow node."""
    
    async def execute_async(self, inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
        """Execute node asynchronously."""
        try:
            if hasattr(self.executor, '__call__'):
                import asyncio
                if asyncio.iscoroutinefunction(self.executor):
                    return await self.executor(inputs, **context)
            return self.executor(inputs, **context)
        except Exception as e:
            raise NodeExecutionError(
                f"Async node {self.node_id} execution failed: {str(e)}"
            ) from e


class NodeExecutionError(Exception):
    """Raised when node execution fails."""
    pass


# Convenience functions for creating common node types
def create_function_node(
    node_id: NodeId,
    func: Callable[..., Dict[str, Any]],
    config: Optional[NodeConfig] = None
) -> Node:
    """Create a node from a Python function."""
    return Node(node_id=node_id, executor=func, config=config)


def create_async_function_node(
    node_id: NodeId,
    func: Callable[..., Dict[str, Any]],
    config: Optional[NodeConfig] = None
) -> AsyncNode:
    """Create an async node from a Python function."""
    return AsyncNode(node_id=node_id, executor=func, config=config)