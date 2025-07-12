"""
Message definitions for LLM communication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any  # Keep Any, ruff might be overly aggressive for other types

from typing_extensions import TypeAlias

# Type aliases
Role: TypeAlias = str
Content: TypeAlias = str
ConditionResult: TypeAlias = bool


@dataclass
class Message:
    """Represents a message in the workflow."""

    role: Role
    content: Content
    name: str | None = None  # UP045
    tool_calls: list[dict[str, Any]] = field(default_factory=list)  # UP006
    tool_call_id: str | None = None  # UP045
    metadata: dict[str, Any] = field(default_factory=dict)  # UP006

    @classmethod
    def user(cls, content: Content, **metadata: Any) -> Message:
        return cls("user", content, metadata=metadata)

    @classmethod
    def assistant(cls, content: Content, **metadata: Any) -> Message:
        return cls("assistant", content, metadata=metadata)

    @classmethod
    def tool(cls, content: Content, name: str, **metadata: Any) -> Message:
        return cls("tool", content, name=name, metadata=metadata)

    @classmethod
    def system(cls, content: Content, **metadata: Any) -> Message:
        return cls("system", content, metadata=metadata)

    def to_dict(self) -> dict[str, Any]:  # UP006
        """Convert to dictionary format."""
        result = {"role": self.role, "content": self.content}
        if self.name is not None:  # Ensure 'name' is only added if it's not None
            result["name"] = self.name
        if self.tool_calls:  # Only add if not empty
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:  # Only add if not None
            result["tool_call_id"] = self.tool_call_id
        if self.metadata:  # Only add if not empty
            result["metadata"] = self.metadata
        return result


@dataclass
class ChatResult:
    """Represents the result of a chat model interaction."""

    message: Message
    usage: dict[str, int]  # UP006
    model: str
    finish_reason: str
    response_id: str | None = None  # UP045
    metadata: dict[str, Any] = field(default_factory=dict)  # UP006

    @property
    def content(self) -> Content:
        return self.message.content

    @property
    def role(self) -> Role:
        return self.message.role

    @property
    def tool_calls(self) -> list[dict[str, Any]]:  # UP006
        return self.message.tool_calls

    @property
    def tool_call_id(self) -> str | None:  # UP045
        return self.message.tool_call_id
