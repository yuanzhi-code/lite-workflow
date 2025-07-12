"""
Edge definitions for workflow connections.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,  # Keep Any, ruff might be overly aggressive for other types
    Callable,
)

from typing_extensions import TypeAlias

from ..definitions.state import State

# Type aliases
ConditionResult: TypeAlias = bool


class EdgeCondition(ABC):
    """Protocol for edge conditions."""

    @abstractmethod
    def __call__(
        self, outputs: dict[str, Any], state: State
    ) -> ConditionResult:  # UP006
        """Evaluate whether this edge should be traversed."""
        ...


@dataclass
class Edge:
    """A directed edge connecting two nodes in a graph."""

    source_id: str
    target_id: str
    condition: EdgeCondition | None = None  # UP045
    metadata: dict[str, Any] = field(default_factory=dict)  # UP006

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    def should_traverse(self, outputs: dict[str, Any], state: State) -> bool:  # UP006
        """Determine if this edge should be traversed."""
        if self.condition is None:
            return True
        return self.condition(outputs, state)

    def __repr__(self) -> str:
        return f"Edge(source='{self.source_id}', target='{self.target_id}')"


@dataclass
class ConditionalEdge(Edge):
    """An edge that is traversed only if a condition is met."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        condition: EdgeCondition,
        metadata: dict[str, Any] | None = None,  # UP045, UP006
    ):
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            condition=condition,
            metadata=metadata,
        )


@dataclass
class WhenCondition(EdgeCondition):
    """An edge condition that checks if a key in the outputs matches an expected value."""

    key: str
    expected_value: Any

    def __call__(self, outputs: dict[str, Any], state: State) -> bool:  # UP006
        """Check if key exists and matches expected value."""
        actual_value = outputs.get(self.key)
        return actual_value == self.expected_value


@dataclass
class FunctionCondition(EdgeCondition):
    """An edge condition based on a custom function."""

    func: Callable[[dict[str, Any], State], bool]  # UP006

    def __call__(self, outputs: dict[str, Any], state: State) -> bool:  # UP006
        return self.func(outputs, state)


def when(key: str, expected_value: Any) -> WhenCondition:
    """Helper function to create a WhenCondition."""
    return WhenCondition(key=key, expected_value=expected_value)


def condition(
    func: Callable[[dict[str, Any], State], bool],
) -> FunctionCondition:  # UP006
    """Helper function to create a FunctionCondition."""
    return FunctionCondition(func=func)
