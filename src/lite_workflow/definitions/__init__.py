"""
Core type definitions for the Lite Workflow system.

This module defines the fundamental building blocks:
- Nodes: Computation units
- Edges: Data/control flow connections
- Graphs: Workflow structures
- Messages: Communication primitives
"""

from .edge import Edge, EdgeCondition
from .graph import Graph, GraphConfig
from .message import ChatResult, Message
from .node import Node, NodeConfig
from .state import State, UpdateStrategy

__all__ = [
    # Core types
    "Node",
    "NodeConfig",
    "Edge",
    "EdgeCondition",
    "Graph",
    "GraphConfig",
    "State",
    "UpdateStrategy",
    # Messages
    "Message",
    "ChatResult",
]
