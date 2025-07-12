"""
Edge definitions for workflow connections.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol
from typing_extensions import TypeAlias

from .state import State

# Type aliases
EdgeId: TypeAlias = str
ConditionResult: TypeAlias = bool


class EdgeCondition(Protocol):
    """Protocol for edge conditions."""
    
    def __call__(self, outputs: Dict[str, Any], state: State) -> ConditionResult:
        """Evaluate whether this edge should be traversed."""
        ...


@dataclass
class Edge:
    """Represents a connection between nodes in a workflow."""
    
    source_id: str
    target_id: str
    condition: Optional[EdgeCondition] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        """Initialize default metadata."""
        if self.metadata is None:
            self.metadata = {}
    
    def should_traverse(self, outputs: Dict[str, Any], state: State) -> bool:
        """Determine if this edge should be traversed."""
        if self.condition is None:
            return True
        
        try:
            return bool(self.condition(outputs, state))
        except Exception as e:
            raise EdgeEvaluationError(
                f"Edge condition evaluation failed: {str(e)}"
            ) from e
    
    def __repr__(self) -> str:
        condition_str = "(conditional)" if self.condition else ""
        return f"Edge({self.source_id} -> {self.target_id}{condition_str})"


class ConditionalEdge(Edge):
    """Edge with explicit condition handling."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        condition: EdgeCondition,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            condition=condition,
            metadata=metadata or {}
        )


class SimpleCondition:
    """Simple condition based on key-value matching."""
    
    def __init__(self, key: str, expected_value: Any):
        self.key = key
        self.expected_value = expected_value
    
    def __call__(self, outputs: Dict[str, Any], state: State) -> bool:
        """Check if key exists and matches expected value."""
        actual_value = outputs.get(self.key)
        if actual_value is None:
            actual_value = state.get(self.key)
        return actual_value == self.expected_value


class LambdaCondition:
    """Condition based on lambda function."""
    
    def __init__(self, func: EdgeCondition):
        self.func = func
    
    def __call__(self, outputs: Dict[str, Any], state: State) -> bool:
        return self.func(outputs, state)


class EdgeEvaluationError(Exception):
    """Raised when edge evaluation fails."""
    pass


# Convenience functions
def when(key: str, value: Any) -> SimpleCondition:
    """Create a simple equality condition."""
    return SimpleCondition(key, value)


def condition(func: EdgeCondition) -> LambdaCondition:
    """Create a lambda-based condition."""
    return LambdaCondition(func)