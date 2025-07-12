"""
Tool-based nodes for workflow execution.

Provides support for tool calling and external integrations with a LangChain-inspired design.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Type

from typing_extensions import TypeAlias

from ..core.logger import Logger
from ..definitions.node import Node

# Type aliases
ToolInput: type = dict[str, Any]
ToolOutput: type = dict[str, Any]
ToolCall: type = dict[str, Any]


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""

    pass


class ToolValidationError(ToolError):
    """Raised when tool input validation fails."""

    pass


@dataclass
class ToolSchema:
    """Schema definition for a tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    required: list[str] = field(default_factory=list)

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(
        self,
        name: str,
        description: str,
        schema: ToolSchema | None = None,
        **kwargs: Any,
    ):
        self.name = name
        self.description = description
        self.schema = schema or self._create_schema()
        self.logger = Logger(f"tool.{name}")

    @abstractmethod
    def _run(self, **kwargs: Any) -> str:
        """Execute the tool synchronously."""
        pass

    @abstractmethod
    async def _arun(self, **kwargs: Any) -> str:
        """Execute the tool asynchronously."""
        pass

    def _create_schema(self) -> ToolSchema:
        """Create schema from tool metadata."""
        # Default schema - subclasses should override
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters={},
            required=[],
        )

    def run(self, *args: Any, **kwargs: Any) -> str:
        """Run the tool with validation."""
        try:
            return self._run(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Tool {self.name} execution failed: {e}")
            raise ToolExecutionError(f"Tool {self.name} failed: {e}") from e

    async def arun(self, *args: Any, **kwargs: Any) -> str:
        """Run the tool asynchronously with validation."""
        try:
            return await self._arun(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Async tool {self.name} execution failed: {e}")
            raise ToolExecutionError(f"Async tool {self.name} failed: {e}") from e

    def __call__(self, *args: Any, **kwargs: Any) -> str:
        """Allow tools to be called directly."""
        return self.run(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class Tool(BaseTool):
    """Concrete tool implementation that wraps a function."""

    def __init__(
        self,
        func: Callable[..., str],
        name: str | None = None,
        description: str | None = None,
        schema: ToolSchema | None = None,
        **kwargs: Any,
    ):
        self.func = func
        self._is_async = asyncio.iscoroutinefunction(func)

        # Use function metadata if not provided
        name = name or func.__name__
        description = description or func.__doc__ or ""

        super().__init__(name=name, description=description, schema=schema, **kwargs)

    def _run(self, **kwargs: Any) -> str:
        """Execute the tool function synchronously."""
        if self._is_async:
            raise ToolExecutionError(f"Tool {self.name} is async, use arun() instead")
        return self.func(**kwargs)

    async def _arun(self, **kwargs: Any) -> str:
        """Execute the tool function asynchronously."""
        if self._is_async:
            return await self.func(**kwargs)
        else:
            # Run sync function in thread pool, support kwargs
            loop = asyncio.get_event_loop()
            func_partial = functools.partial(self.func, **kwargs)
            return await loop.run_in_executor(None, func_partial)

    def _create_schema(self) -> ToolSchema:
        """Create schema from function signature."""
        sig = inspect.signature(self.func)
        parameters = {}
        required = []

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            param_info = {
                "type": "string",  # Default type
                "description": f"Parameter {name}",
            }

            if param.default == param.empty:
                required.append(name)

            parameters[name] = param_info

        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters=parameters,
            required=required,
        )


def tool(
    name: str | None = None,
    description: str | None = None,
    schema: ToolSchema | None = None,
) -> Callable[[Callable[..., str]], Tool]:
    """Decorator to create a tool from a function."""

    def decorator(func: Callable[..., str]) -> Tool:
        return Tool(func, name=name, description=description, schema=schema)

    return decorator


class ToolRegistry:
    """Registry for managing tools with advanced features."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self.logger = Logger("tool_registry")

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        if tool.name in self._tools:
            self.logger.warning(f"Tool {tool.name} already registered, overwriting")
        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")

    def register_tool(
        self,
        func: Callable[..., str] | Tool,
        name: str | None = None,
        description: str | None = None,
        schema: ToolSchema | None = None,
    ) -> Tool:
        """Register a function as a tool."""
        if isinstance(func, Tool):
            # If it's already a Tool object, register it directly
            self.register(func)
            return func
        else:
            # Create a new Tool from function
            tool_obj = Tool(func, name=name, description=description, schema=schema)
            self.register(tool_obj)
            return tool_obj

    def get_tool(self, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_tools(self) -> list[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_tools_for_openai(self) -> list[dict[str, Any]]:
        """Get tools in OpenAI format."""
        return [tool.schema.to_openai_format() for tool in self._tools.values()]

    def execute_tool(self, name: str, **kwargs: Any) -> str:
        """Execute a tool by name."""
        tool_obj = self.get_tool(name)
        if not tool_obj:
            raise ToolError(f"Tool '{name}' not found")
        return tool_obj.run(**kwargs)

    async def aexecute_tool(self, name: str, **kwargs: Any) -> str:
        """Execute a tool asynchronously by name."""
        tool_obj = self.get_tool(name)
        if not tool_obj:
            raise ToolError(f"Tool '{name}' not found")
        return await tool_obj.arun(**kwargs)

    def unregister(self, name: str) -> None:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            self.logger.info(f"Unregistered tool: {name}")


class ToolExecutor:
    """Executor for handling tool calls with LLM integration."""

    def __init__(self, registry: ToolRegistry, model: Any | None = None):
        self.registry = registry
        self.model = model
        self.logger = Logger("tool_executor")

    def execute_tool_call(self, tool_call: ToolCall) -> dict[str, Any]:
        """Execute a single tool call."""
        try:
            name = tool_call.get("function", {}).get("name")
            arguments = tool_call.get("function", {}).get("arguments", {})

            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            self.logger.info(f"Executing tool: {name} with args: {arguments}")
            result = self.registry.execute_tool(name, **arguments)

            return {
                "tool_call_id": tool_call.get("id"),
                "name": name,
                "result": result,
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return {
                "tool_call_id": tool_call.get("id"),
                "name": name,
                "result": str(e),
                "status": "error",
            }

    async def aexecute_tool_call(self, tool_call: ToolCall) -> dict[str, Any]:
        """Execute a single tool call asynchronously."""
        try:
            name = tool_call.get("function", {}).get("name")
            arguments = tool_call.get("function", {}).get("arguments", {})

            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            self.logger.info(f"Executing async tool: {name} with args: {arguments}")
            result = await self.registry.aexecute_tool(name, **arguments)

            return {
                "tool_call_id": tool_call.get("id"),
                "name": name,
                "result": result,
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Async tool execution failed: {e}")
            return {
                "tool_call_id": tool_call.get("id"),
                "name": name,
                "result": str(e),
                "status": "error",
            }

    def execute_tool_calls(self, tool_calls: list[ToolCall]) -> list[dict[str, Any]]:
        """Execute multiple tool calls."""
        results = []
        for tool_call in tool_calls:
            result = self.execute_tool_call(tool_call)
            results.append(result)
        return results

    async def aexecute_tool_calls(
        self, tool_calls: list[ToolCall]
    ) -> list[dict[str, Any]]:
        """Execute multiple tool calls asynchronously."""
        tasks = [self.aexecute_tool_call(tool_call) for tool_call in tool_calls]
        return await asyncio.gather(*tasks)


class ToolNode(Node):
    """Node that can execute tools with LLM integration."""

    def __init__(
        self,
        node_id: str,
        tool_registry: ToolRegistry,
        model: Any | None = None,
        **kwargs: Any,
    ):
        self.tool_registry = tool_registry
        self.model = model
        self.executor = ToolExecutor(tool_registry, model)
        self.logger = Logger(f"tool_node.{node_id}")

        super().__init__(node_id=node_id, executor=self._execute_tools, **kwargs)

    def _execute_tools(self, inputs: dict[str, Any], **context: Any) -> dict[str, Any]:
        """Execute tools based on inputs."""
        prompt = inputs.get("prompt", "")
        tool_calls = inputs.get("tool_calls", [])

        if not tool_calls:
            # No tool calls, return available tools info
            tools = self.tool_registry.get_tools_for_openai()
            return {
                "prompt": prompt,
                "available_tools": [tool["function"]["name"] for tool in tools],
                "tool_count": len(tools),
                "message": "No tool calls provided",
            }

        # Execute tool calls
        results = self.executor.execute_tool_calls(tool_calls)

        return {
            "prompt": prompt,
            "tool_results": results,
            "executed_tools": [r["name"] for r in results if r["status"] == "success"],
            "failed_tools": [r["name"] for r in results if r["status"] == "error"],
        }


# Convenience functions
def create_tool_registry() -> ToolRegistry:
    """Create a new tool registry."""
    return ToolRegistry()


def register_tool(
    registry: ToolRegistry,
    func: Callable[..., str],
    name: str | None = None,
    description: str | None = None,
) -> Tool:
    """Register a function as a tool in the registry."""
    return registry.register_tool(func, name=name, description=description)
