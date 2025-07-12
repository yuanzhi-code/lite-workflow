"""
Advanced state management with conflict resolution and event handling.
"""

from __future__ import annotations

import threading
from typing import Any, Callable

from typing_extensions import TypeAlias

from ..definitions.state import InMemoryState, State, UpdateStrategy
from .event_bus import Event, EventBus

StateKey: TypeAlias = str
StateValue: TypeAlias = Any
MergeStrategy: TypeAlias = Callable[[StateValue, StateValue], StateValue]


class StateUpdateEvent(Event):
    """Event emitted when state is updated."""

    def __init__(
        self,
        key: StateKey,
        old_value: StateValue,
        new_value: StateValue,
        source: str,
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(
            event_type="state_update",
            data={
                "key": key,
                "old_value": old_value,
                "new_value": new_value,
                "source": source,
                "metadata": metadata or {},
            },
        )


class StateManager:
    """Thread-safe state management with conflict resolution."""

    def __init__(
        self,
        initial_state: dict[StateKey, StateValue] | None = None,
        event_bus: EventBus | None = None,
    ):
        self._state = InMemoryState(initial_state)
        self._event_bus = event_bus or EventBus()
        self._lock = threading.RLock()
        self._merge_strategies: dict[StateKey, MergeStrategy] = {}

    def get_state(self) -> State:
        """Get current state (read-only view)."""
        with self._lock:
            return InMemoryState(self._state.to_dict())

    def get(self, key: StateKey, default: StateValue = None) -> StateValue:
        """Get state value by key."""
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: StateKey, value: StateValue, source: str = "unknown") -> None:
        with self._lock:
            old_value = self._state.get(key)
            self._state.set(key, value)

            self._event_bus.emit(
                StateUpdateEvent(
                    key=key, old_value=old_value, new_value=value, source=source
                )
            )

    def update(
        self,
        updates: dict[StateKey, StateValue],
        strategy: UpdateStrategy = UpdateStrategy.OVERWRITE,
        source: str = "unknown",
    ) -> None:
        """Update multiple state values with conflict resolution."""
        with self._lock:
            for key, new_value in updates.items():
                if strategy == UpdateStrategy.OVERWRITE:
                    self.set(key, new_value, source)
                elif strategy == UpdateStrategy.MERGE:
                    self._merge_value(key, new_value, source)
                elif strategy == UpdateStrategy.IGNORE:
                    if key not in self._state:
                        self.set(key, new_value, source)
                elif strategy == UpdateStrategy.RAISE:
                    if key in self._state:
                        raise KeyError(f"Key '{key}' already exists")
                    self.set(key, new_value, source)

    def _merge_value(self, key: StateKey, new_value: StateValue, source: str) -> None:
        """Merge values using registered strategy or intelligent defaults."""
        old_value = self._state.get(key)

        if key in self._merge_strategies:
            merged = self._merge_strategies[key](old_value, new_value)
        elif isinstance(old_value, dict) and isinstance(new_value, dict):
            merged = {**old_value, **new_value}
        elif isinstance(old_value, list) and isinstance(new_value, list):
            merged = old_value + new_value
        else:
            merged = new_value

        self.set(key, merged, source)

    def register_merge_strategy(self, key: StateKey, strategy: MergeStrategy) -> None:
        """Register custom merge strategy for a key."""
        with self._lock:
            self._merge_strategies[key] = strategy

    def snapshot(self) -> dict[StateKey, StateValue]:
        """Create a snapshot of current state."""
        with self._lock:
            return self._state.to_dict()

    def restore(self, snapshot: dict[StateKey, StateValue]) -> None:
        """Restore state from snapshot."""
        with self._lock:
            self._state.clear()
            self._state.update(snapshot)

    def keys(self) -> list[StateKey]:
        """Get all state keys."""
        with self._lock:
            return list(self._state.to_dict().keys())

    def clear(self, source: str = "unknown") -> None:
        """Clear all state."""
        with self._lock:
            keys = list(self._state.to_dict().keys())
            self._state.clear()

            for key in keys:
                self._event_bus.emit(
                    StateUpdateEvent(
                        key=key, old_value=None, new_value=None, source=source
                    )
                )

    def __len__(self) -> int:
        """Return number of keys in state."""
        with self._lock:
            return len(self._state)

    def __repr__(self) -> str:
        return f"StateManager(keys={len(self)})"
