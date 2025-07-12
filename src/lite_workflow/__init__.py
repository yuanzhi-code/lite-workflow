"""
Lite Workflow - A modern workflow management system inspired by Pregel.

This package provides a clean, type-safe interface for building complex
LLM workflows with graph-based execution patterns.
"""

__version__ = "0.1.0"
__author__ = "Lite Workflow Team"


# Local application imports
from .components import OpenAIChatModel, PythonFunctionNode, ToolNode
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
]
