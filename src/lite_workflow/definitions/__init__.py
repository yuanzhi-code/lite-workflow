"""
Core type definitions for the Lite Workflow system.

This module defines the fundamental building blocks:
- Nodes: Computation units
- Edges: Data/control flow connections  
- Graphs: Workflow structures
- Messages: Communication primitives
"""

from .node import Node, NodeConfig
from .edge import Edge, EdgeCondition
from .graph import Graph, GraphConfig
from .state import State, UpdateStrategy
from .message import Message, ChatResult

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