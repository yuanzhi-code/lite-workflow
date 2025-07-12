"""
Function-based nodes for workflow execution.

Provides convenient wrappers for Python functions as workflow nodes.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable

from ..definitions.node import Node, create_function_node  # Force reload

# Removed create_node as create_function_node now handles both sync/async
# def create_node(
#     node_id: str,
#     func: Callable[..., Any],
#     is_async: bool = False,
#     **kwargs: Any
# ) -> Node:
#     """Create a node from any Python function."""

#     def node_executor(inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
#         """Wrapper to handle function execution."""
#         try:
#             result = func(inputs, **context)

#             # Handle both sync and async results
#             if asyncio.iscoroutine(result):
#                 raise ValueError(
#                     f"Async function {func.__name__} must be used with AsyncNode"
#                 )

#             # Ensure result is a dictionary
#             if not isinstance(result, dict):
#                 result = {"output": result}

#             return result

#         except Exception as e:
#             raise RuntimeError(f"Function node {node_id} failed: {e}")

#     def async_node_executor(inputs: Dict[str, Any], **context: Any) -> Dict[str, Any]:
#         """Async wrapper for async functions."""
#         # This will be handled by AsyncNode
#         return func(inputs, **context)

#     if is_async:
#         return AsyncNode(
#             node_id=node_id,
#             executor=async_node_executor,
#             **kwargs
#         )
#     else:
#         return Node(
#             node_id=node_id,
#             executor=node_executor,
#             **kwargs
#         )


class PythonFunctionNode:
    """Convenient wrapper for Python function nodes."""

    def __init__(self, func: Callable[..., Any], node_id: str | None = None):
        self.func = func
        self.node_id = node_id or func.__name__

    def to_node(self) -> Node:
        """Convert to workflow BaseNode."""
        return create_function_node(self.node_id, self.func)

    def __call__(self, *args, **kwargs) -> Any:
        """Allow direct function calls."""
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"PythonFunctionNode(id='{self.node_id}', func={self.func.__name__})"


class AsyncPythonFunctionNode:
    """Convenient wrapper for async Python function nodes."""

    def __init__(self, func: Callable[..., Any], node_id: str | None = None):
        self.func = func
        self.node_id = node_id or func.__name__

    def to_node(self) -> Node:
        """Convert to workflow BaseNode."""
        return create_function_node(self.node_id, self.func)

    async def __call__(self, *args, **kwargs) -> Any:
        """Allow direct async function calls."""
        return await self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return (
            f"AsyncPythonFunctionNode(id='{self.node_id}', func={self.func.__name__})"
        )


# Decorators for easy node creation
def node(node_id: str | None = None):
    """Decorator to create a Python function node."""

    def decorator(func: Callable[..., Any]) -> Node:
        return create_function_node(node_id or func.__name__, func)

    return decorator


def async_node(node_id: str | None = None):
    """Decorator to create an async Python function node."""

    def decorator(func: Callable[..., Any]) -> Node:
        return create_function_node(node_id or func.__name__, func)

    return decorator


# Utility decorators for timing and logging
def timed_node(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to add timing to node functions."""

    @wraps(func)
    def wrapper(inputs: dict[str, Any], **context: Any) -> dict[str, Any]:
        start_time = time.time()
        result = func(inputs, **context)
        duration = time.time() - start_time

        if isinstance(result, dict):
            result["__duration"] = duration
        else:
            result = {"output": result, "__duration": duration}

        return result

    return wrapper


def logging_node(logger: Any):
    """Decorator to add logging to node functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(inputs: dict[str, Any], **context: Any) -> dict[str, Any]:
            logger.info(f"Executing node {func.__name__}")
            try:
                result = func(inputs, **context)
                logger.info(f"Node {func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Node {func.__name__} failed: {e}")
                raise

        return wrapper

    return decorator
