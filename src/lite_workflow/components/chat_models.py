"""
Modern ChatModel implementations with elegant interfaces.

This module provides clean, LangChain-inspired implementations for OpenAI
and OpenAI-compatible chat models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Iterator

import openai

from ..definitions.message import ChatResult, Message


class BaseChatModel(ABC):
    """Abstract base class for all chat models."""

    @abstractmethod
    def invoke(self, messages: str | list[Message], **kwargs: Any) -> ChatResult:
        """Generate a single response synchronously."""
        pass

    @abstractmethod
    def stream(
        self, messages: str | list[Message], **kwargs: Any
    ) -> Iterator[ChatResult]:
        """Stream responses synchronously."""
        pass

    @abstractmethod
    async def ainvoke(self, messages: str | list[Message], **kwargs: Any) -> ChatResult:
        """Generate a single response asynchronously."""
        pass

    @abstractmethod
    async def astream(
        self, messages: str | list[Message], **kwargs: Any
    ) -> AsyncIterator[ChatResult]:
        """Stream responses asynchronously."""
        pass


@dataclass
class SimpleChatModel(BaseChatModel):
    """A simple chat model that wraps another chat model and provides basic routing."""

    model: BaseChatModel
    kwargs: dict[str, Any]

    def invoke(self, messages: str | list[Message], **kwargs: Any) -> ChatResult:
        """Generate a single response."""
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.model.invoke(messages, **merged_kwargs)

    def stream(
        self, messages: str | list[Message], **kwargs: Any
    ) -> Iterator[ChatResult]:
        """Stream responses."""
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.model.stream(messages, **merged_kwargs)

    async def ainvoke(self, messages: str | list[Message], **kwargs: Any) -> ChatResult:
        """Async generate a single response."""
        merged_kwargs = {**self.kwargs, **kwargs}
        return await self.model.ainvoke(messages, **merged_kwargs)

    async def astream(
        self, messages: str | list[Message], **kwargs: Any
    ) -> AsyncIterator[ChatResult]:
        """Async stream responses."""
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.model.astream(messages, **merged_kwargs)


class OpenAIChatModel(BaseChatModel):
    """OpenAI chat model implementation."""

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _prepare_messages(self, messages: str | list[Message]) -> list[dict[str, Any]]:
        """Convert various input formats to OpenAI format."""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        return [msg.to_dict() for msg in messages]

    def _create_params(
        self, messages: list[dict[str, Any]], **kwargs: Any
    ) -> dict[str, Any]:
        """Create parameters for API call."""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": False,
        }
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        params.update(kwargs)
        return params

    def invoke(self, messages: str | list[Message], **kwargs: Any) -> ChatResult:
        """Generate a single response."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        response = self.client.chat.completions.create(**params)
        msg_content = response.choices[0].message.content or ""
        return ChatResult(
            message=Message.assistant(msg_content),
            usage=response.usage.model_dump(),
            model=response.model,
            finish_reason=response.choices[0].finish_reason,
            response_id=response.id,
        )

    def stream(
        self, messages: str | list[Message], **kwargs: Any
    ) -> Iterator[ChatResult]:
        """Stream responses."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        params["stream"] = True

        for chunk in self.client.chat.completions.create(**params):
            if chunk.choices and chunk.choices[0].delta.content:
                yield ChatResult(
                    message=Message.assistant(chunk.choices[0].delta.content),
                    usage={},
                    model=chunk.model,
                    finish_reason=chunk.choices[0].finish_reason,
                    response_id=chunk.id,
                )

    async def ainvoke(self, messages: str | list[Message], **kwargs: Any) -> ChatResult:
        """Async generate a single response."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        # Use asyncio.to_thread to run the synchronous API call in a thread
        import asyncio

        response = await asyncio.to_thread(
            self.client.chat.completions.create, **params
        )
        msg_content = response.choices[0].message.content or ""
        return ChatResult(
            message=Message.assistant(msg_content),
            usage=response.usage.model_dump(),
            model=response.model,
            finish_reason=response.choices[0].finish_reason,
            response_id=response.id,
        )

    async def astream(
        self, messages: str | list[Message], **kwargs: Any
    ) -> AsyncIterator[ChatResult]:
        """Async stream responses."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        params["stream"] = True

        # Use asyncio.to_thread to run the synchronous streaming API call in a thread
        import asyncio

        response = await asyncio.to_thread(
            self.client.chat.completions.create, **params
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield ChatResult(
                    message=Message.assistant(chunk.choices[0].delta.content),
                    usage={},
                    model=chunk.model,
                    finish_reason=chunk.choices[0].finish_reason,
                    response_id=chunk.id,
                )


# Convenience factory functions
def ChatOpenAI(**kwargs: Any) -> OpenAIChatModel:
    """Factory function for creating OpenAI chat models."""
    return OpenAIChatModel(**kwargs)


def ChatSiliconFlow(model: str = "Qwen/Qwen3-8B", **kwargs: Any) -> OpenAIChatModel:
    """Factory for SiliconFlow OpenAI-compatible API."""
    return OpenAIChatModel(
        model=model, base_url="https://api.siliconflow.cn/v1", **kwargs
    )
