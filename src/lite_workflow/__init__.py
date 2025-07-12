"""
Lite Workflow - A modern workflow management system inspired by Pregel.

This package provides a clean, type-safe interface for building complex
LLM workflows with graph-based execution patterns.
"""

__version__ = "0.1.0"
__author__ = "Lite Workflow Team"


# Local application imports
from .components import (
    BaseTool,
    OpenAIChatModel,
    PythonFunctionNode,
    Tool,
    ToolExecutor,
    ToolNode,
    ToolRegistry,
    create_tool_registry,
    register_tool,
    tool,
)
from .core import ErrorHandler, StateManager
from .definitions import (
    ChatResult,
    Edge,
    Graph,
    Message,
    Node,
    NodeConfig,
    State,
    UpdateStrategy,
)
from .engine import ExecutionEngine, PregelEngine, Workflow

__all__ = [
    # Core types
    "Node",
    "NodeConfig",
    "Edge",
    "Graph",
    "State",
    "UpdateStrategy",
    "Message",
    "ChatResult",
    # Core modules
    "StateManager",
    "ErrorHandler",
    "ExecutionEngine",
    "PregelEngine",
    "Workflow",
    # Components
    "OpenAIChatModel",
    "PythonFunctionNode",
    "ToolNode",
    # Tools
    "BaseTool",
    "Tool",
    "ToolRegistry",
    "ToolExecutor",
    "create_tool_registry",
    "register_tool",
    "tool",
]
