"""
Event-driven architecture for workflow execution.
"""

from __future__ import annotations

import inspect
import threading
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Event:
    """Base class for all events in the system."""

    event_type: str
    data: dict[str, Any]
    timestamp: float | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = (
                threading.local()._time if hasattr(threading.local(), "_time") else 0.0
            )


class EventHandler:
    """Abstract base class for event handlers."""

    async def handle(self, event: Event) -> None:
        """Handle an event."""
        pass


class EventBus:
    """A simple, thread-safe event bus for publishing and subscribing to events."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
        self._global_handlers: list[Callable] = []

    def on(self, event_type: str, handler: Callable) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def on_global(self, handler: Callable) -> None:
        """Register a handler for all events."""
        self._global_handlers.append(handler)

    def off(self, event_type: str, handler: Callable) -> None:
        """Unregister a handler for a specific event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass

    def off_any(self, handler: Callable) -> None:
        """Unregister a global handler."""
        try:
            self._global_handlers.remove(handler)
        except ValueError:
            pass

    def emit(self, event: Event) -> None:
        """Emit an event to all registered handlers."""
        # Handle type-specific handlers
        for handler in self._handlers.get(event.event_type, []):
            handler(event)

        # Handle global handlers
        for handler in self._global_handlers:
            handler(event)

    async def emit_async(self, event: Event) -> None:
        """Emit an event asynchronously."""
        # Handle global handlers
        for handler in self._global_handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Error in global handler: {e}")

        # Handle specific type handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    if inspect.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"Error in handler for {event.event_type}: {e}")

    def clear(self) -> None:
        """Clear all handlers."""
        self._handlers.clear()
        self._global_handlers.clear()

    def get_handler_count(self, event_type: str = None) -> int:
        """Get number of handlers for an event type."""
        if event_type is None:
            return len(self._global_handlers) + sum(
                len(handlers) for handlers in self._handlers.values()
            )
        return len(self._handlers.get(event_type, [])) + len(self._global_handlers)
