"""
Abstract execution engine interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..core.error_handler import ErrorHandler
from ..core.logger import Logger
from ..core.state_manager import StateManager
from ..definitions.graph import Graph


@dataclass
class ExecutionConfig:
    """Configuration for workflow execution."""

    max_iterations: int = 1000
    timeout: float | None = None
    enable_parallel: bool = False
    checkpoint_interval: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ExecutionEngine(ABC):
    """Abstract base class for all workflow execution engines."""

    def __init__(
        self,
        graph: Graph,
        state_manager: StateManager,
        error_handler: ErrorHandler,
        config: ExecutionConfig | None = None,
    ):
        self.graph = graph
        self.state_manager = state_manager
        self.error_handler = error_handler
        self.config = config or ExecutionConfig()
        self.logger = Logger("execution_engine")

    @abstractmethod
    def execute(self) -> Any:
        """Execute the workflow."""
        pass

    @abstractmethod
    def get_execution_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        pass
