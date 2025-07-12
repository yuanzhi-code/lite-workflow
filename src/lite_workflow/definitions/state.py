"""
State management for workflow execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from typing_extensions import TypeAlias

# Type aliases
StateKey: TypeAlias = str
StateValue: TypeAlias = Any


class State(ABC):
    """Abstract base class for state management."""

    @abstractmethod
    def get(self, key: StateKey, default: StateValue = None) -> StateValue:
        """Get state value by key."""
        pass

    @abstractmethod
    def set(self, key: StateKey, value: StateValue) -> None:
        """Set state value for a given key."""
        pass

    @abstractmethod
    def update(self, updates: dict[StateKey, StateValue]) -> None:
        """Update multiple state values."""
        pass

    @abstractmethod
    def delete(self, key: StateKey) -> None:
        """Delete state value by key."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[StateKey, StateValue]:
        """Convert state to dictionary."""
        pass


class UpdateStrategy(Enum):
    """Strategies for updating state."""
    OVERWRITE = "overwrite"
    MERGE = "merge"
    IGNORE = "ignore"
    RAISE = "raise"


@dataclass
class InMemoryState(State):
    """Simple in-memory state implementation."""

    def __init__(self, initial_data: dict[StateKey, StateValue] | None = None):
        self._data: dict[StateKey, StateValue] = initial_data or {}

    def get(self, key: StateKey, default: StateValue = None) -> StateValue:
        return self._data.get(key, default)

    def set(self, key: StateKey, value: StateValue) -> None:
        self._data[key] = value

    def update(self, updates: dict[StateKey, StateValue]) -> None:
        """Update multiple state values."""
        self._data.update(updates)

    def delete(self, key: StateKey) -> None:
        """Delete state value by key."""
        self._data.pop(key, None)

    def to_dict(self) -> dict[StateKey, StateValue]:
        """Convert state to dictionary."""
        return self._data.copy()

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"InMemoryState({len(self)} keys)"
