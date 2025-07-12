"""
Modern ChatModel implementations with elegant interfaces.

This module provides clean, LangChain-inspired implementations for OpenAI
and OpenAI-compatible chat models.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union
from dataclasses import dataclass

import openai
from openai import AsyncOpenAI, OpenAI

from ..definitions.message import Message, ChatResult


class BaseChatModel(ABC):
    """Abstract base class for chat models."""
    
    @abstractmethod
    def invoke(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> ChatResult:
        """Generate a single response synchronously."""
        pass
    
    @abstractmethod
    def stream(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> Iterator[ChatResult]:
        """Stream responses synchronously."""
        pass
    
    @abstractmethod
    async def ainvoke(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> ChatResult:
        """Generate a single response asynchronously."""
        pass
    
    @abstractmethod
    async def astream(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> AsyncIterator[ChatResult]:
        """Stream responses asynchronously."""
        pass
    
    def bind(self, **kwargs: Any) -> "RunnableBinding":
        """Bind default parameters to the model."""
        return RunnableBinding(model=self, kwargs=kwargs)


@dataclass
class RunnableBinding:
    """Allows binding default parameters to a model."""
    model: BaseChatModel
    kwargs: Dict[str, Any]
    
    def invoke(self, messages: Union[str, List[Message]], **kwargs: Any) -> ChatResult:
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.model.invoke(messages, **merged_kwargs)
    
    def stream(self, messages: Union[str, List[Message]], **kwargs: Any) -> Iterator[ChatResult]:
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.model.stream(messages, **merged_kwargs)
    
    async def ainvoke(self, messages: Union[str, List[Message]], **kwargs: Any) -> ChatResult:
        merged_kwargs = {**self.kwargs, **kwargs}
        return await self.model.ainvoke(messages, **merged_kwargs)
    
    async def astream(self, messages: Union[str, List[Message]], **kwargs: Any) -> AsyncIterator[ChatResult]:
        merged_kwargs = {**self.kwargs, **kwargs}
        async for chunk in self.model.astream(messages, **merged_kwargs):
            yield chunk


class OpenAIChatModel(BaseChatModel):
    """Modern OpenAI chat model with elegant interface."""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ):
        self.model = model
        self.default_params = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # Resolve API credentials
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        # Initialize clients
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def _prepare_messages(self, messages: Union[str, List[Message]]) -> List[Dict[str, Any]]:
        """Convert various input formats to OpenAI format."""
        if isinstance(messages, str):
            return [Message.user(messages).to_dict()]
        
        return [msg.to_dict() for msg in messages]
    
    def _create_params(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Create parameters for API call."""
        params = {
            "model": self.model,
            "messages": messages,
            **self.default_params,
            **kwargs
        }
        return {k: v for k, v in params.items() if v is not None}
    
    def _parse_response(self, response: Any) -> ChatResult:
        """Parse OpenAI response into ChatResult."""
        choice = response.choices[0]
        message = choice.message
        
        return ChatResult(
            message=Message(
                role=message.role,
                content=message.content or "",
                tool_calls=[tool.model_dump() for tool in (message.tool_calls or [])]
            ),
            usage=response.usage.model_dump() if response.usage else {},
            model=response.model,
            finish_reason=choice.finish_reason or "stop",
            response_id=response.id
        )
    
    def invoke(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> ChatResult:
        """Generate a single response."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        
        try:
            response = self.client.chat.completions.create(**params)
            return self._parse_response(response)
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}") from e
    
    def stream(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> Iterator[ChatResult]:
        """Stream responses."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        params["stream"] = True
        
        try:
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield ChatResult(
                        message=Message(
                            role="assistant",
                            content=chunk.choices[0].delta.content
                        ),
                        usage=chunk.usage.model_dump() if chunk.usage else {},
                        model=chunk.model,
                        finish_reason=chunk.choices[0].finish_reason or "",
                        response_id=chunk.id
                    )
        except Exception as e:
            raise RuntimeError(f"OpenAI streaming failed: {str(e)}") from e
    
    async def ainvoke(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> ChatResult:
        """Async generate a single response."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        
        try:
            response = await self.async_client.chat.completions.create(**params)
            return self._parse_response(response)
        except Exception as e:
            raise RuntimeError(f"Async OpenAI API call failed: {str(e)}") from e
    
    async def astream(
        self,
        messages: Union[str, List[Message]],
        **kwargs: Any
    ) -> AsyncIterator[ChatResult]:
        """Async stream responses."""
        openai_messages = self._prepare_messages(messages)
        params = self._create_params(openai_messages, **kwargs)
        params["stream"] = True
        
        try:
            stream = await self.async_client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield ChatResult(
                        message=Message(
                            role="assistant",
                            content=chunk.choices[0].delta.content
                        ),
                        usage=chunk.usage.model_dump() if chunk.usage else {},
                        model=chunk.model,
                        finish_reason=chunk.choices[0].finish_reason or "",
                        response_id=chunk.id
                    )
        except Exception as e:
            raise RuntimeError(f"Async OpenAI streaming failed: {str(e)}") from e
    
    def __repr__(self) -> str:
        return f"OpenAIChatModel(model='{self.model}', base_url='{self.base_url}')"


# Convenience factory functions
def ChatOpenAI(**kwargs: Any) -> OpenAIChatModel:
    """Factory function for creating OpenAI chat models."""
    return OpenAIChatModel(**kwargs)


def ChatSiliconFlow(model: str = "Qwen/Qwen3-8B", **kwargs: Any) -> OpenAIChatModel:
    """Factory for SiliconFlow OpenAI-compatible API."""
    return OpenAIChatModel(
        model=model,
        base_url="https://api.siliconflow.cn/v1",
        **kwargs
    )