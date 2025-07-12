"""
State management for workflow execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Callable, Union
from typing_extensions import TypeAlias

# Type aliases
StateKey: TypeAlias = str
StateValue: TypeAlias = Any


class UpdateStrategy(Enum):
    """Strategies for handling state conflicts."""
    OVERWRITE = "overwrite"
    MERGE = "merge"
    IGNORE = "ignore"
    RAISE = "raise"


class State(ABC):
    """Abstract base class for workflow state."""
    
    @abstractmethod
    def get(self, key: StateKey, default: StateValue = None) -> StateValue:
        """Get state value by key."""
        pass
    
    @abstractmethod
    def set(self, key: StateKey, value: StateValue) -> None:
        """Set state value by key."""
        pass
    
    @abstractmethod
    def update(self, updates: Dict[StateKey, StateValue]) -> None:
        """Update multiple state values."""
        pass
    
    @abstractmethod
    def delete(self, key: StateKey) -> None:
        """Delete a state key."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[StateKey, StateValue]:
        """Convert state to dictionary."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all state."""
        pass
    
    def __getitem__(self, key: StateKey) -> StateValue:
        """Allow dict-like access: state[key]."""
        return self.get(key)
    
    def __setitem__(self, key: StateKey, value: StateValue) -> None:
        """Allow dict-like assignment: state[key] = value."""
        self.set(key, value)
    
    def __contains__(self, key: StateKey) -> bool:
        """Check if key exists in state."""
        return self.get(key) is not None


class InMemoryState(State):
    """Simple in-memory state implementation."""
    
    def __init__(self, initial_data: Optional[Dict[StateKey, StateValue]] = None):
        self._data: Dict[StateKey, StateValue] = initial_data or {}
    
    def get(self, key: StateKey, default: StateValue = None) -> StateValue:
        """Get state value by key."""
        return self._data.get(key, default)
    
    def set(self, key: StateKey, value: StateValue) -> None:
        """Set state value by key."""
        self._data[key] = value
    
    def update(self, updates: Dict[StateKey, StateValue]) -> None:
        """Update multiple state values."""
        self._data.update(updates)
    
    def delete(self, key: StateKey) -> None:
        """Delete a state key."""
        self._data.pop(key, None)
    
    def to_dict(self) -> Dict[StateKey, StateValue]:
        """Convert state to dictionary."""
        return self._data.copy()
    
    def clear(self) -> None:
        """Clear all state."""
        self._data.clear()
    
    def __len__(self) -> int:
        """Return number of keys in state."""
        return len(self._data)
    
    def __repr__(self) -> str:
        return f"InMemoryState(keys={len(self._data)})"