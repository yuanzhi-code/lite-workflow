#!/usr/bin/env python3
"""
Elegant workflow examples demonstrating the new beautiful API.
"""

import asyncio
from lite_workflow import Workflow, ChatOpenAI, ChatSiliconFlow
from lite_workflow.components.function_nodes import node
from lite_workflow.definitions.edge import when


# Example 1: Simple LLM Chain
@node("data_processor")
def process_data(inputs: dict) -> dict:
    """Process input data."""
    prompt = inputs.get("prompt", "")
    return {"processed": f"Processing: {prompt}"}


@node("llm_caller")
def call_llm(inputs: dict) -> dict:
    """Call LLM with processed data."""
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    prompt = inputs.get("processed", "")
    result = model.invoke(prompt)
    return {"response": result.content}


# Example 2: Conditional Workflow
@node("decision_maker")
def make_decision(inputs: dict) -> dict:
    """Make a decision based on input."""
    value = inputs.get("value", 0)
    return {"decision": "high" if value > 50 else "low"}


@node("high_processor")
def process_high(inputs: dict) -> dict:
    """Process high values."""
    return {"result": "Processing high value"}


@node("low_processor")
def process_low(inputs: dict) -> dict:
    """Process low values."""
    return {"result": "Processing low value"}


# Example 3: Complex LLM Integration
@node("content_generator")
def generate_content(inputs: dict) -> dict:
    """Generate content using LLM."""
    topic = inputs.get("topic", "technology")
    model = ChatSiliconFlow(model="Qwen/Qwen3-8B")
    
    prompt = f"Write a brief summary about {topic}"
    result = model.invoke(prompt, max_tokens=100)
    
    return {
        "generated_content": result.content,
        "token_usage": result.usage
    }


@node("content_refiner")
def refine_content(inputs: dict) -> dict:
    """Refine generated content."""
    content = inputs.get("generated_content", "")
    model = ChatOpenAI(model="gpt-4", temperature=0.3)
    
    prompt = f"Refine this content to be more concise: {content}"
    result = model.invoke(prompt, max_tokens=50)
    
    return {"refined_content": result.content}


def run_simple_workflow():
    """Run a simple linear workflow."""
    print("=== Simple Workflow ===")
    
    workflow = Workflow("simple", {"prompt": "Explain quantum computing"})
    workflow.chain("data_processor", "llm_caller")
    
    result = workflow.run()
    print(f"Success: {result.success}")
    print(f"Response: {result.final_state.get('response', 'N/A')}")
    print()


def run_conditional_workflow():
    """Run a workflow with conditional edges."""
    print("=== Conditional Workflow ===")
    
    workflow = Workflow("conditional", {"value": 75})
    workflow.add_node("decision_maker", make_decision)
    workflow.add_node("high_processor", process_high)
    workflow.add_node("low_processor", process_low)
    
    workflow.add_edge("decision_maker", "high_processor")
    workflow.add_edge("decision_maker", "low_processor")
    
    result = workflow.run()
    print(f"Success: {result.success}")
    print(f"Result: {result.final_state.get('result', 'N/A')}")
    print()


def run_complex_workflow():
    """Run a complex LLM workflow."""
    print("=== Complex LLM Workflow ===")
    
    workflow = Workflow("complex", {"topic": "artificial intelligence"})
    workflow.chain("content_generator", "content_refiner")
    
    result = workflow.run()
    print(f"Success: {result.success}")
    print(f"Original: {result.final_state.get('generated_content', 'N/A')[:100]}...")
    print(f"Refined: {result.final_state.get('refined_content', 'N/A')}")
    print(f"Token Usage: {result.final_state.get('token_usage', {})}")
    print()


async def run_async_workflow():
    """Run workflow asynchronously."""
    print("=== Async Workflow ===")
    
    from lite_workflow.engine.pregel_engine import PregelEngine
    from lite_workflow.core.state_manager import StateManager
    from lite_workflow.core.error_handler import ErrorHandler
    from lite_workflow.definitions.graph import Graph
    from lite_workflow.definitions.node import Node
    from lite_workflow.definitions.edge import Edge
    
    # Create async nodes
    async def async_processor(inputs: dict) -> dict:
        await asyncio.sleep(0.1)  # Simulate async work
        return {"processed": "async data"}
    
    # Build graph
    nodes = [
        Node("start", lambda x: {"data": x.get("input", "test")}),
        Node("process", async_processor),
        Node("finish", lambda x: {"result": x.get("processed", "")})
    ]
    
    edges = [
        Edge("start", "process"),
        Edge("process", "finish")
    ]
    
    graph = Graph("async_demo", nodes, edges, "start")
    
    state_manager = StateManager({"input": "async workflow"})
    error_handler = ErrorHandler()
    
    engine = PregelEngine(graph, state_manager, error_handler)
    final_state = await engine.execute_async()
    
    print(f"Async Result: {final_state.get('result', 'N/A')}")
    stats = engine.get_execution_stats()
    print(f"Async Stats: {stats}")


def main():
    """Run all examples."""
    print("🚀 Lite Workflow - Elegant Examples")
    print("=" * 50)
    
    run_simple_workflow()
    run_conditional_workflow()
    run_complex_workflow()
    
    # Run async example
    asyncio.run(run_async_workflow())


if __name__ == "__main__":
    main()