"""
Comprehensive error handling and recovery for workflow execution.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Callable, List, Union
from typing_extensions import TypeAlias

from ..definitions.node import NodeId
from .event_bus import EventBus, Event

# Type aliases
ErrorHandlerFunc: TypeAlias = Callable[[NodeId, Exception, Dict[str, Any]], None]
RetryPolicyFunc: TypeAlias = Callable[[int], float]  # Returns delay in seconds


class ErrorPolicy(Enum):
    """Error handling policies."""
    FAIL_FAST = "fail_fast"
    RETRY = "retry"
    SKIP = "skip"
    CUSTOM = "custom"


@dataclass
class NodeErrorEvent(Event):
    """Event emitted when a node execution fails."""
    
    def __init__(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any],
        retry_count: int = 0,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            event_type="node_error",
            data={
                "node_id": node_id,
                "error": str(error),
                "error_type": type(error).__name__,
                "context": context,
                "retry_count": retry_count,
                "metadata": metadata or {}
            }
        )


@dataclass
class RecoveryEvent(Event):
    """Event emitted when error recovery is attempted."""
    
    def __init__(
        self,
        node_id: NodeId,
        recovery_action: str,
        success: bool,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            event_type="recovery",
            data={
                "node_id": node_id,
                "recovery_action": recovery_action,
                "success": success,
                "metadata": metadata or {}
            }
        )


class ErrorHandler:
    """Centralized error handling and recovery for workflow execution."""
    
    def __init__(
        self,
        default_policy: ErrorPolicy = ErrorPolicy.RETRY,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        event_bus: Optional[EventBus] = None
    ):
        self.default_policy = default_policy
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.event_bus = event_bus or EventBus()
        
        self._node_policies: Dict[NodeId, ErrorPolicy] = {}
        self._node_handlers: Dict[NodeId, ErrorHandlerFunc] = {}
        self._custom_retry_policies: Dict[NodeId, RetryPolicyFunc] = {}
        
        # Set up default logger
        self.logger = logging.getLogger(__name__)
    
    def set_node_policy(self, node_id: NodeId, policy: ErrorPolicy) -> None:
        """Set error handling policy for a specific node."""
        self._node_policies[node_id] = policy
    
    def set_node_handler(
        self,
        node_id: NodeId,
        handler: ErrorHandlerFunc
    ) -> None:
        """Set custom error handler for a specific node."""
        self._node_handlers[node_id] = handler
    
    def set_retry_policy(
        self,
        node_id: NodeId,
        policy: RetryPolicyFunc
    ) -> None:
        """Set custom retry policy for a specific node."""
        self._custom_retry_policies[node_id] = policy
    
    def get_retry_delay(self, node_id: NodeId, attempt: int) -> float:
        """Calculate retry delay based on policy."""
        if node_id in self._custom_retry_policies:
            return self._custom_retry_policies[node_id](attempt)
        
        # Exponential backoff with jitter
        delay = self.base_delay * (self.backoff_factor ** attempt)
        jitter = 0.1 * delay * (hash(node_id) % 1000 / 1000)
        return delay + jitter
    
    async def handle_error_async(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any],
        attempt: int = 0
    ) -> Union[Dict[str, Any], None]:
        """Handle node error asynchronously."""
        self.event_bus.emit(NodeErrorEvent(
            node_id=node_id,
            error=error,
            context=context,
            retry_count=attempt
        ))
        
        policy = self._node_policies.get(node_id, self.default_policy)
        
        if policy == ErrorPolicy.FAIL_FAST:
            self.logger.error(f"Node {node_id} failed: {error}")
            raise error
        
        elif policy == ErrorPolicy.SKIP:
            self.logger.warning(f"Skipping node {node_id} due to error: {error}")
            self.event_bus.emit(RecoveryEvent(
                node_id=node_id,
                recovery_action="skip",
                success=True
            ))
            return {"error": str(error), "skipped": True}
        
        elif policy == ErrorPolicy.RETRY and attempt < self.max_retries:
            return await self._retry_async(node_id, error, context, attempt)
        
        elif policy == ErrorPolicy.CUSTOM and node_id in self._node_handlers:
            return await self._handle_custom_async(node_id, error, context)
        
        # Fallback: fail
        self.logger.error(f"Node {node_id} failed permanently: {error}")
        raise error
    
    def handle_error_sync(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any],
        attempt: int = 0
    ) -> Union[Dict[str, Any], None]:
        """Handle node error synchronously."""
        # Similar to async version but synchronous
        self.event_bus.emit(NodeErrorEvent(
            node_id=node_id,
            error=error,
            context=context,
            retry_count=attempt
        ))
        
        policy = self._node_policies.get(node_id, self.default_policy)
        
        if policy == ErrorPolicy.FAIL_FAST:
            self.logger.error(f"Node {node_id} failed: {error}")
            raise error
        
        elif policy == ErrorPolicy.SKIP:
            self.logger.warning(f"Skipping node {node_id} due to error: {error}")
            self.event_bus.emit(RecoveryEvent(
                node_id=node_id,
                recovery_action="skip",
                success=True
            ))
            return {"error": str(error), "skipped": True}
        
        elif policy == ErrorPolicy.RETRY and attempt < self.max_retries:
            return self._retry_sync(node_id, error, context, attempt)
        
        elif policy == ErrorPolicy.CUSTOM and node_id in self._node_handlers:
            return self._handle_custom_sync(node_id, error, context)
        
        # Fallback: fail
        self.logger.error(f"Node {node_id} failed permanently: {error}")
        raise error
    
    async def _retry_async(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any],
        attempt: int
    ) -> Dict[str, Any]:
        """Retry node execution asynchronously."""
        delay = self.get_retry_delay(node_id, attempt)
        self.logger.info(f"Retrying node {node_id} in {delay:.2f}s (attempt {attempt + 1})")
        
        await asyncio.sleep(delay)
        
        # This would typically involve re-executing the node
        # For now, return retry instruction
        return {"retry": True, "attempt": attempt + 1, "delay": delay}
    
    def _retry_sync(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any],
        attempt: int
    ) -> Dict[str, Any]:
        """Retry node execution synchronously."""
        delay = self.get_retry_delay(node_id, attempt)
        self.logger.info(f"Retrying node {node_id} in {delay:.2f}s (attempt {attempt + 1})")
        
        time.sleep(delay)
        
        return {"retry": True, "attempt": attempt + 1, "delay": delay}
    
    async def _handle_custom_async(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle error with custom handler."""
        handler = self._node_handlers[node_id]
        if asyncio.iscoroutinefunction(handler):
            return await handler(node_id, error, context)
        else:
            return handler(node_id, error, context)
    
    def _handle_custom_sync(
        self,
        node_id: NodeId,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle error with custom handler."""
        handler = self._node_handlers[node_id]
        return handler(node_id, error, context)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error handling configuration."""
        return {
            "default_policy": self.default_policy.value,
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "backoff_factor": self.backoff_factor,
            "custom_policies": len(self._node_policies),
            "custom_handlers": len(self._node_handlers),
            "custom_retry_policies": len(self._custom_retry_policies)
        }