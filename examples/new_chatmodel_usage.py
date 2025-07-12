"""
Usage examples for the new LangChain-style ChatModel.
Demonstrates elegant patterns and clean API design.
"""

import asyncio
from components.langchain_style_chatmodel import (
    OpenAIChatModel, 
    ChatOpenAI, 
    ChatSiliconFlow,
    Message
)


def basic_usage_example():
    """Basic synchronous usage."""
    print("=== Basic Usage ===")
    
    # Create model with default settings
    model = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Simple string input
    result = model.invoke("Hello, how are you?")
    print(f"Response: {result.content}")
    print(f"Usage: {result.usage}")
    print()


def message_chain_example():
    """Using Message objects for more control."""
    print("=== Message Chain ===")
    
    model = ChatOpenAI(model="gpt-4")
    
    messages = [
        Message.system("You are a helpful assistant."),
        Message.human("What's the weather like today?"),
        Message.ai("I'd be happy to help you check the weather!"),
        Message.human("In San Francisco, please.")
    ]
    
    result = model.invoke(messages)
    print(f"AI Response: {result.content}")
    print()


def parameter_binding_example():
    """Using bind() for reusable configurations."""
    print("=== Parameter Binding ===")
    
    # Create base model with specific settings
    base_model = ChatOpenAI()
    creative_model = base_model.bind(temperature=0.9, max_tokens=150)
    precise_model = base_model.bind(temperature=0.1, max_tokens=50)
    
    prompt = "Tell me a short story about AI."
    
    creative_result = creative_model.invoke(prompt)
    precise_result = precise_model.invoke(prompt)
    
    print(f"Creative (temp=0.9): {creative_result.content}")
    print(f"Precise (temp=0.1): {precise_result.content}")
    print()


def streaming_example():
    """Streaming responses."""
    print("=== Streaming ===")
    
    model = ChatOpenAI()
    
    print("Streaming response:")
    for chunk in model.stream("Tell me about artificial intelligence in 3 sentences."):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n")


async def async_usage_example():
    """Async usage patterns."""
    print("=== Async Usage ===")
    
    model = ChatOpenAI()
    
    # Async invoke
    result = await model.ainvoke("What is machine learning?")
    print(f"Async result: {result.content[:50]}...")
    
    # Async streaming
    print("Async streaming:")
    async for chunk in model.astream("Explain quantum computing briefly."):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n")


def siliconflow_example():
    """Using SiliconFlow OpenAI-compatible API."""
    print("=== SiliconFlow Usage ===")
    
    # Factory function for convenience
    model = ChatSiliconFlow(model="Qwen/Qwen3-8B")
    
    result = model.invoke("你好，请介绍一下自己")
    print(f"SiliconFlow response: {result.content}")
    print()


def chain_pattern_example():
    """Example of chaining operations."""
    print("=== Chain Pattern ===")
    
    # Create specialized models
    translator = ChatOpenAI(model="gpt-4").bind(
        temperature=0.3,
        system_message="You are a professional translator. Translate to Chinese."
    )
    
    summarizer = ChatOpenAI().bind(
        temperature=0.5,
        max_tokens=100,
        system_message="Summarize the following text concisely."
    )
    
    text = "Artificial Intelligence is transforming industries worldwide."
    
    # Chain operations
    translated = translator.invoke(text)
    summary = summarizer.invoke(translated.content)
    
    print(f"Original: {text}")
    print(f"Translated: {translated.content}")
    print(f"Summary: {summary.content}")
    print()


async def main():
    """Run all examples."""
    basic_usage_example()
    message_chain_example()
    parameter_binding_example()
    streaming_example()
    siliconflow_example()
    chain_pattern_example()
    
    await async_usage_example()


if __name__ == "__main__":
    asyncio.run(main())