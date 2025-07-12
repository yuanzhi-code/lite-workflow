#!/usr/bin/env python3
"""
Graph Structure Demo - A beautiful workflow showcasing fan-out/fan-in, loops, and conditional edges.

This demo creates a complex workflow that:
1. Processes initial data
2. Fan-outs to multiple LLM paths (summarization, analysis, creative)
3. Aggregates results
4. Loops for quality improvement
5. Final processing
"""

import asyncio
from lite_workflow import Workflow, ChatOpenAI, Message
from lite_workflow.components.function_nodes import node
from lite_workflow.definitions.edge import when


# 🎯 Node Functions

@node("initial_processor")
def initial_processor(inputs: dict) -> dict:
    """Process initial input and prepare for fan-out."""
    prompt = inputs.get("prompt", "Explain artificial intelligence")
    print(f"📝 Initial processor: {prompt}")
    return {
        "original_prompt": prompt,
        "processed_prompt": prompt.strip(),
        "iteration": 0
    }


@node("summarizer")
def create_summary(inputs: dict) -> dict:
    """Create a concise summary using LLM."""
    prompt = inputs.get("processed_prompt", "")
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    messages = [
        Message.system("You are a concise expert summarizer."),
        Message.user(f"Summarize this in 2-3 sentences: {prompt}")
    ]
    
    result = model.invoke(messages)
    print(f"📊 Summarizer: {result.content[:50]}...")
    return {"summary": result.content, "path": "summary"}


@node("analyst")
def create_analysis(inputs: dict) -> dict:
    """Create detailed analysis using LLM."""
    prompt = inputs.get("processed_prompt", "")
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    messages = [
        Message.system("You are an expert analyst."),
        Message.user(f"Provide detailed analysis of: {prompt}")
    ]
    
    result = model.invoke(messages)
    print(f"🔍 Analyst: {result.content[:50]}...")
    return {"analysis": result.content, "path": "analysis"}


@node("creative_writer")
def create_creative(inputs: dict) -> dict:
    """Create creative content using LLM."""
    prompt = inputs.get("processed_prompt", "")
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9)
    
    messages = [
        Message.system("You are a creative writer."),
        Message.user(f"Write a creative story about: {prompt}")
    ]
    
    result = model.invoke(messages)
    print(f"✨ Creative: {result.content[:50]}...")
    return {"creative": result.content, "path": "creative"}


@node("aggregator")
def aggregate_results(inputs: dict) -> dict:
    """Aggregate results from all paths."""
    results = inputs if isinstance(inputs, dict) else {}
    
    # Collect all results
    summary = results.get("summary", "")
    analysis = results.get("analysis", "")
    creative = results.get("creative", "")
    
    aggregated = {
        "summary": summary,
        "analysis": analysis,
        "creative": creative,
        "combined": f"Summary: {summary[:100]}... Analysis: {analysis[:100]}... Creative: {creative[:100]}..."
    }
    
    print(f"🎯 Aggregator: Combined {len(aggregated)} results")
    return aggregated


@node("final_processor")
def final_processing(inputs: dict) -> dict:
    """Final processing of the refined content."""
    final_content = inputs.get("combined", "")
    iteration = inputs.get("iteration", 0)
    
    print(f"🎉 Final processing: {len(final_content)} chars after {iteration} iterations")
    
    return {
        "final_content": final_content,
        "final_iteration": iteration,
        "content_length": len(final_content),
        "quality_score": inputs.get("quality_score", 0)
    }


# 🏗️ Graph Construction

def create_demo_graph() -> Workflow:
    """Create the demonstration graph."""
    workflow = Workflow("demo_graph", {"prompt": "The future of artificial intelligence"})
    
    # Add all nodes
    workflow.add_node("initial_processor", initial_processor)
    workflow.add_node("summarizer", create_summary)
    workflow.add_node("analyst", create_analysis)
    workflow.add_node("creative_writer", create_creative)
    workflow.add_node("aggregator", aggregate_results)
    workflow.add_node("final_processor", final_processing)
    
    # 🔄 Build the graph structure
    # 1. Initial processing
    workflow.add_edge("initial_processor", "summarizer")
    workflow.add_edge("initial_processor", "analyst")
    workflow.add_edge("initial_processor", "creative_writer")
    
    # 2. Fan-in to aggregator
    workflow.add_edge("summarizer", "aggregator")
    workflow.add_edge("analyst", "aggregator")
    workflow.add_edge("creative_writer", "aggregator")
    
    # 3. Final processing
    workflow.add_edge("aggregator", "final_processor")
    
    return workflow


# 🚀 Execution Functions

def run_demo():
    """Run the graph demo synchronously."""
    print("🎯 Lite Workflow Graph Demo")
    print("=" * 50)
    
    workflow = create_demo_graph()
    print(f"📊 Workflow: {workflow}")
    
    print("\n🔄 Starting execution...")
    result = workflow.run()
    
    print(f"\n✅ Execution Complete!")
    print(f"Success: {result.success}")
    
    if result.success:
        final_state = result.final_state.to_dict()
        print(f"\n📝 Final Results:")
        print(f"   Final Content: {final_state.get('final_content', 'N/A')[:200]}...")
        print(f"   Iterations: {final_state.get('final_iteration', 0)}")
        print(f"   Quality Score: {final_state.get('quality_score', 0):.1f}%")
        print(f"   Content Length: {final_state.get('content_length', 0)} chars")
        
        print(f"\n📈 Execution Stats:")
        stats = result.execution_stats
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Error: {result.error}")


async def run_async_demo():
    """Run the graph demo asynchronously."""
    print("🎯 Async Graph Demo")
    print("=" * 50)
    
    from lite_workflow.engine.pregel_engine import PregelEngine
    from lite_workflow.core.state_manager import StateManager
    from lite_workflow.core.error_handler import ErrorHandler
    from lite_workflow.definitions.graph import Graph
    from lite_workflow.definitions.node import Node
    from lite_workflow.definitions.edge import Edge
    
    # Create a simpler async graph
    nodes = [
        Node("start", lambda x: {"value": len(x.get("input", "AI"))}),
        Node("double", lambda x: {"value": x["value"] * 2}),
        Node("triple", lambda x: {"value": x["value"] * 3}),
        Node("aggregate", lambda x: {"result": f"Final: {x.get('value', 0)}"})
    ]
    
    edges = [
        Edge("start", "double"),
        Edge("start", "triple"),
        Edge("double", "aggregate"),
        Edge("triple", "aggregate")
    ]
    
    graph = Graph("async_demo", nodes, edges, "start")
    
    state_manager = StateManager({"input": "Artificial Intelligence"})
    error_handler = ErrorHandler()
    
    engine = PregelEngine(graph, state_manager, error_handler)
    
    print("🔄 Running async execution...")
    final_state = await engine.execute_async()
    
    print(f"✅ Async Complete!")
    print(f"Result: {final_state.to_dict()}")
    stats = engine.get_execution_stats()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    run_demo()
    
    # Uncomment to run async demo
    # asyncio.run(run_async_demo())