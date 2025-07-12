"""
Structured logging for workflow execution.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime


class Logger:
    """Structured logger for workflow execution."""
    
    def __init__(
        self,
        name: str = "lite_workflow",
        level: int = logging.INFO,
        format_string: Optional[str] = None
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_workflow_start(self, workflow_id: str, metadata: Dict[str, Any] = None) -> None:
        """Log workflow start."""
        self.logger.info(
            f"Workflow started",
            extra={"workflow_id": workflow_id, "metadata": metadata or {}}
        )
    
    def log_node_execution(
        self,
        node_id: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration: float
    ) -> None:
        """Log node execution completion."""
        self.logger.info(
            f"Node {node_id} executed successfully",
            extra={
                "node_id": node_id,
                "inputs": inputs,
                "outputs": outputs,
                "duration": duration
            }
        )
    
    def log_node_error(
        self,
        node_id: str,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Log node execution error."""
        self.logger.error(
            f"Node {node_id} failed: {str(error)}",
            extra={"node_id": node_id, "error": str(error), "context": context},
            exc_info=True
        )
    
    def log_workflow_complete(
        self,
        workflow_id: str,
        duration: float,
        final_state: Dict[str, Any]
    ) -> None:
        """Log workflow completion."""
        self.logger.info(
            f"Workflow completed",
            extra={
                "workflow_id": workflow_id,
                "duration": duration,
                "final_state": final_state
            }
        )
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Debug logging."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Info logging."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Warning logging."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Error logging."""
        self.logger.error(message, extra=kwargs)
    
    def set_level(self, level: int) -> None:
        """Set logging level."""
        self.logger.setLevel(level)