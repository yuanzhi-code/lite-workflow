"""
Abstract execution engine interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

from ..definitions.graph import Graph
from ..definitions.state import State
from ..core.state_manager import StateManager
from ..core.error_handler import ErrorHandler


@dataclass
class ExecutionConfig:
    """Configuration for workflow execution."""
    max_iterations: int = 1000
    timeout: Optional[float] = None
    enable_parallel: bool = False
    checkpoint_interval: int = 10
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ExecutionEngine(ABC):
    """Abstract base class for workflow execution engines."""
    
    def __init__(
        self,
        graph: Graph,
        state_manager: StateManager,
        error_handler: ErrorHandler,
        config: Optional[ExecutionConfig] = None
    ):
        self.graph = graph
        self.state_manager = state_manager
        self.error_handler = error_handler
        self.config = config or ExecutionConfig()
    
    @abstractmethod
    async def execute_async(self) -> State:
        """Execute the workflow asynchronously."""
        pass
    
    @abstractmethod
    def execute(self) -> State:
        """Execute the workflow synchronously."""
        pass
    
    @abstractmethod
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        pass
    
    def validate(self) -> bool:
        """Validate the graph and configuration."""
        return self.graph.validate_cycles()