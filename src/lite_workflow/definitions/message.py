"""
Message definitions for LLM communication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from typing_extensions import TypeAlias

Role: TypeAlias = str
Content: TypeAlias = str


@dataclass
class Message:
    """A message in a conversation."""
    
    role: Role
    content: Content
    name: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def system(cls, content: str, **metadata: Any) -> Message:
        """Create a system message."""
        return cls(role="system", content=content, metadata=metadata)
    
    @classmethod
    def user(cls, content: str, **metadata: Any) -> Message:
        """Create a user message."""
        return cls(role="user", content=content, metadata=metadata)
    
    @classmethod
    def assistant(cls, content: str, **metadata: Any) -> Message:
        """Create an assistant message."""
        return cls(role="assistant", content=content, metadata=metadata)
    
    @classmethod
    def human(cls, content: str, **metadata: Any) -> Message:
        """Alias for user message."""
        return cls.user(content, **metadata)
    
    @classmethod
    def ai(cls, content: str, **metadata: Any) -> Message:
        """Alias for assistant message."""
        return cls.assistant(content, **metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result
    
    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"


@dataclass
class ChatResult:
    """Result from a chat model."""
    
    message: Message
    usage: Dict[str, int]
    model: str
    finish_reason: str
    response_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def content(self) -> str:
        """Get message content."""
        return self.message.content
    
    @property
    def role(self) -> str:
        """Get message role."""
        return self.message.role
    
    def __str__(self) -> str:
        return f"{self.model}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"