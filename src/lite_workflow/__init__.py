"""
Lite Workflow - A modern workflow management system inspired by Pregel.

This package provides a clean, type-safe interface for building complex
LLM workflows with graph-based execution patterns.
"""

__version__ = "0.1.0"
__author__ = "Lite Workflow Team"

from .definitions import *
from .core import *
from .engine import *
from .components import *

__all__ = [
    # Core types
    "Node",
    "Edge", 
    "Graph",
    "State",
    "Workflow",
    "ExecutionEngine",
    "StateManager",
    "ErrorHandler",
    # Components
    "OpenAIChatModel",
    "PythonFunctionNode",
    # Utils
    "Message",
    "ChatResult",
]