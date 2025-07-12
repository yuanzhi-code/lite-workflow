"""
Event-driven architecture for workflow execution.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Event:
    """Base event class."""
    event_type: str
    data: Dict[str, Any]
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event."""
        pass


class EventBus:
    """Simple event bus for workflow events."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._global_handlers: List[Callable] = []
    
    def on(self, event_type: str, handler: Callable) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def on_any(self, handler: Callable) -> None:
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
        """Emit an event synchronously."""
        # Handle global handlers
        for handler in self._global_handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    # For sync context, we can't await async handlers
                    pass
                else:
                    handler(event)
            except Exception as e:
                print(f"Error in global handler: {e}")
        
        # Handle specific type handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    if inspect.iscoroutinefunction(handler):
                        # For sync context, we can't await async handlers
                        pass
                    else:
                        handler(event)
                except Exception as e:
                    print(f"Error in handler for {event.event_type}: {e}")
    
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
            return len(self._global_handlers) + sum(len(handlers) for handlers in self._handlers.values())
        return len(self._handlers.get(event_type, [])) + len(self._global_handlers)