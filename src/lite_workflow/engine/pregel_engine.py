"""
Pregel-style execution engine with superstep computation.
Implements the "think like a vertex" paradigm for workflow execution.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from ..core.event_bus import Event, EventBus
from ..core.logger import Logger
from ..definitions.graph import NodeId
from ..definitions.state import State
from .execution_engine import ExecutionEngine


@dataclass
class SuperStepEvent(Event):
    """Event emitted at the start/end of a superstep."""

    def __init__(
        self,
        superstep: int,
        active_nodes: list[NodeId],
        completed_nodes: list[NodeId],
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(
            event_type="superstep",
            data={
                "superstep": superstep,
                "active_nodes": active_nodes,
                "completed_nodes": completed_nodes,
                "metadata": metadata or {},
            },
        )


@dataclass
class NodeExecutionEvent(Event):
    """Event emitted when a node completes execution."""

    def __init__(
        self,
        node_id: NodeId,
        duration: float,
        outputs: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(
            event_type="node_execution",
            data={
                "node_id": node_id,
                "duration": duration,
                "outputs": outputs,
                "metadata": metadata or {},
            },
        )


class PregelEngine(ExecutionEngine):
    """
    Pregel-style execution engine implementing superstep computation.

    Each superstep consists of:
    1. Node activation (vertices that received messages)
    2. Node execution (compute function)
    3. Message passing (send messages to neighbors)
    4. State synchronization
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = Logger("pregel_engine")
        self.event_bus = EventBus()
        self._execution_stats = {
            "start_time": None,
            "end_time": None,
            "total_supersteps": 0,
            "total_nodes_executed": 0,
            "node_execution_times": {},
            "messages_sent": 0,
        }

    async def execute_async(self) -> State:
        """Execute workflow asynchronously using supersteps."""
        start_time = time.time()
        self._execution_stats["start_time"] = start_time

        self.logger.log_workflow_start(self.graph.graph_id)

        # Initialize execution state
        current_messages = self._initialize_messages()
        superstep = 0

        while superstep < self.config.max_iterations:
            # Check termination conditions
            if not any(current_messages.values()):
                break

            # Execute superstep
            new_messages = await self._execute_superstep_async(
                current_messages, superstep
            )

            current_messages = new_messages
            superstep += 1
            self._execution_stats["total_supersteps"] = superstep

        end_time = time.time()
        self._execution_stats["end_time"] = end_time

        final_state = self.state_manager.get_state()
        self.logger.log_workflow_complete(
            self.graph.graph_id, end_time - start_time, final_state.to_dict()
        )

        return final_state

    def execute(self) -> State:
        """Execute workflow synchronously."""
        # Run async version in sync context
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.execute_async())
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(self.execute_async())

    def _initialize_messages(self) -> dict[NodeId, list[dict[str, Any]]]:
        """Initialize message queues for the first superstep."""
        messages = defaultdict(list)

        # Send initial state to start node
        start_node = self.graph.start_node
        initial_data = self.state_manager.get_state().to_dict()
        messages[start_node].append(initial_data)

        return messages

    async def _execute_superstep_async(
        self, messages: dict[NodeId, list[dict[str, Any]]], superstep: int
    ) -> dict[NodeId, list[dict[str, Any]]]:
        """Execute a single superstep asynchronously."""
        active_nodes = [node_id for node_id, msgs in messages.items() if msgs]

        print(f"⚙️ 超步 {superstep}: 活跃节点 {active_nodes}")

        self.event_bus.emit(
            SuperStepEvent(
                superstep=superstep, active_nodes=active_nodes, completed_nodes=[]
            )
        )

        # Execute all active nodes in parallel
        tasks = []
        for node_id in active_nodes:
            task = self._execute_node_async(node_id, messages[node_id], superstep)
            tasks.append(task)

        # Wait for all executions to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect new messages
        new_messages = defaultdict(list)
        completed_nodes = []

        for node_id, result in zip(active_nodes, results):
            if isinstance(result, Exception):
                # Handle error
                try:
                    recovery_result = await self.error_handler.handle_error_async(
                        node_id, result, {"superstep": superstep}
                    )
                    if recovery_result:
                        result = recovery_result
                    else:
                        continue
                except Exception as e:
                    raise RuntimeError(f"Node {node_id} failed permanently: {e}") from e

            completed_nodes.append(node_id)

            # Send messages to neighbors
            node_outputs = result
            outgoing_edges = self.graph.get_outgoing_edges(node_id)

            for edge in outgoing_edges:
                if edge.should_traverse(node_outputs, self.state_manager.get_state()):
                    new_messages[edge.target_id].append(node_outputs)
                    self._execution_stats["messages_sent"] += 1

        # Update execution stats
        self.event_bus.emit(
            SuperStepEvent(
                superstep=superstep,
                active_nodes=active_nodes,
                completed_nodes=completed_nodes,
            )
        )

        return new_messages

    async def _execute_node_async(
        self, node_id: NodeId, messages: list[dict[str, Any]], superstep: int
    ) -> dict[str, Any]:
        """Execute a single node asynchronously."""
        node = self.graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        # Aggregate messages
        aggregated_input = {}
        for message in messages:
            aggregated_input.update(message)

        print(f"ℹ️ 节点 {node_id} (超步 {superstep}) 聚合输入: {aggregated_input}")

        # Add current state context
        full_context = {
            **self.state_manager.get_state().to_dict(),
            **aggregated_input,
            "__superstep": superstep,
            "__node_id": node_id,
        }

        # Execute node
        start_time = time.time()

        try:
            outputs = await node.execute_async(full_context)

            # Update global state
            self.state_manager.update(outputs, source=f"node_{node_id}")

            duration = time.time() - start_time
            self._execution_stats["node_execution_times"][node_id] = duration
            self._execution_stats["total_nodes_executed"] += 1

            return outputs

        except Exception as e:
            raise RuntimeError(f"Node {node_id} execution failed: {e}") from e

    def get_execution_stats(self) -> dict[str, Any]:
        """Get comprehensive execution statistics."""
        stats = self._execution_stats.copy()
        stats["total_duration"] = stats["end_time"] - stats["start_time"]
        return stats

    def get_progress(self) -> dict[str, Any]:
        """Get current execution progress."""
        total_nodes = len(self.graph)
        completed_nodes = self._execution_stats["total_nodes_executed"]
        progress_percent = (
            (completed_nodes / total_nodes) * 100 if total_nodes > 0 else 0
        )
        return {
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "progress_percent": progress_percent,
            "total_supersteps": self._execution_stats["total_supersteps"],
            "messages_sent": self._execution_stats["messages_sent"],
        }
