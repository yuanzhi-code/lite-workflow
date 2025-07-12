#!/usr/bin/env python3
"""
Comprehensive Graph Demo - Fan-in/Fan-out, Conditional Edges, and Loops

This demo showcases all advanced graph patterns:
1. Fan-out: Single node to multiple parallel nodes
2. Fan-in: Multiple nodes converging to single node
3. Conditional edges: Dynamic routing based on results
4. Loops: Iterative refinement with quality gates
5. State management across supersteps
"""

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

import time

from lite_workflow.core.error_handler import ErrorHandler
from lite_workflow.core.state_manager import StateManager
from lite_workflow.definitions.edge import Edge

# Import from our new architecture
from lite_workflow.definitions.graph import Graph
from lite_workflow.definitions.node import create_function_node
from lite_workflow.engine.pregel_engine import PregelEngine

# 🎯 Node Implementations


def initial_processor(inputs: dict) -> dict:
    """Process initial input and prepare for fan-out."""
    prompt = inputs.get("prompt", "Explain machine learning to a 10-year-old")
    print(f"📝 [开始] 处理: {prompt}")
    return {
        "original_prompt": prompt,
        "processed_prompt": prompt.strip(),
        "timestamp": time.time(),
    }


def parallel_processor_a(inputs: dict) -> dict:
    """First parallel processing branch."""
    prompt = inputs.get("processed_prompt", "")
    print("🔍 [分支 A] 处理分支 A")
    return {
        "branch_a": f"分支 A 分析: {prompt[:50]}...",
        "complexity_score": len(prompt) // 10,
    }


def parallel_processor_b(inputs: dict) -> dict:
    """Second parallel processing branch."""
    prompt = inputs.get("processed_prompt", "")
    print("🎨 [分支 B] 处理分支 B")
    return {
        "branch_b": f"分支 B 创意: {prompt[:50]}...",
        "creativity_score": len(prompt) // 5,
    }


def parallel_processor_c(inputs: dict) -> dict:
    """Third parallel processing branch."""
    prompt = inputs.get("processed_prompt", "")
    print("⚡ [分支 C] 处理分支 C")
    return {
        "branch_c": f"分支 C 技术: {prompt[:50]}...",
        "technical_score": len(prompt) // 8,
    }


def fan_in_aggregator(inputs: dict) -> dict:
    """Aggregate results from all parallel branches."""
    print("🎯 [聚合] 聚合并行结果")

    # Collect all branch results
    branches = {}
    for key, value in inputs.items():
        if key.startswith("branch_"):
            branches[key] = value

    scores = {
        "complexity": inputs.get("complexity_score", 0),
        "creativity": inputs.get("creativity_score", 0),
        "technical": inputs.get("technical_score", 0),
    }

    aggregated = {
        "branches": branches,
        "scores": scores,
        "total_score": sum(scores.values()),
        "quality_threshold": 50,
    }

    print(f"   已聚合 {len(branches)} 个分支，总分: {aggregated['total_score']}")
    return aggregated


def quality_gate(inputs: dict) -> dict:
    """Check if quality meets threshold and decide if loop continues."""
    total_score = inputs.get("total_score", 0)
    threshold = inputs.get("quality_threshold", 50)
    iteration = inputs.get("iteration", 0)

    meets_quality = total_score >= threshold
    should_continue = iteration < 3 and not meets_quality  # Max 3 iterations

    print(f"⚖️ [质量门] 得分: {total_score}/{threshold}, 继续: {should_continue}")

    return {
        "meets_quality": meets_quality,
        "should_continue": should_continue,
        "iteration": iteration,
        "total_score": total_score,
    }


def improvement_engine(inputs: dict) -> dict:
    """Improve the content quality."""
    iteration = inputs.get("iteration", 0)
    branches = inputs.get("branches", {})

    print(f"🔧 [改进] 提升质量 (迭代 {iteration + 1})")

    # Simulate improvement by increasing scores
    improved = {
        "branches": {k: v + " [IMPROVED]" for k, v in branches.items()},
        "scores": {
            "complexity": 15 + iteration * 5,
            "creativity": 20 + iteration * 8,
            "technical": 12 + iteration * 6,
        },
        "iteration": iteration + 1,
        "quality_threshold": 50,
    }

    improved["total_score"] = sum(improved["scores"].values())
    return improved


def final_renderer(inputs: dict) -> dict:
    """Final rendering of the processed content."""
    branches = inputs.get("branches", {})
    total_score = inputs.get("total_score", 0)
    iteration = inputs.get("iteration", 0)

    print("🎉 [完成] 渲染完成内容")

    final_content = {
        "final_output": {
            "summary": "Combined processing complete",
            "branches_processed": len(branches),
            "final_score": total_score,
            "iterations_needed": iteration,
            "branches": branches,
        },
        "metadata": {
            "process_complete": True,
            "quality_achieved": total_score >= 50,
            "execution_time": time.time(),
        },
    }

    return final_content


# 🏗️ Graph Structure Builder


def create_comprehensive_graph() -> Graph:
    """Create the comprehensive demo graph with all patterns."""

    # Create nodes
    nodes = [
        create_function_node("initial_processor", initial_processor),
        create_function_node("parallel_processor_a", parallel_processor_a),
        create_function_node("parallel_processor_b", parallel_processor_b),
        create_function_node("parallel_processor_c", parallel_processor_c),
        create_function_node("fan_in_aggregator", fan_in_aggregator),
        create_function_node("quality_gate", quality_gate),
        create_function_node("improvement_engine", improvement_engine),
        create_function_node("final_renderer", final_renderer),
    ]

    # Create edges with all patterns
    edges = [
        # Initial processing
        Edge("initial_processor", "parallel_processor_a"),
        Edge("initial_processor", "parallel_processor_b"),
        Edge("initial_processor", "parallel_processor_c"),
        # Fan-in aggregation
        Edge("parallel_processor_a", "fan_in_aggregator"),
        Edge("parallel_processor_b", "fan_in_aggregator"),
        Edge("parallel_processor_c", "fan_in_aggregator"),
        # Quality gate
        Edge("fan_in_aggregator", "quality_gate"),
        # Conditional loop
        Edge(
            "quality_gate",
            "improvement_engine",
            condition=lambda outputs, state: outputs.get("should_continue", False),
        ),
        Edge("improvement_engine", "quality_gate"),
        # Final processing when quality met
        Edge(
            "quality_gate",
            "final_renderer",
            condition=lambda outputs, state: not outputs.get("should_continue", True)
            and outputs.get("meets_quality", False),
        ),
    ]

    return Graph("comprehensive_demo", nodes, edges, "initial_processor")


# 🚀 Execution Functions


def run_comprehensive_demo():
    """Run the comprehensive demo."""
    print("🎯 综合图演示 - 所有模式")
    print("=" * 60)

    # Build the graph
    graph = create_comprehensive_graph()
    print(f"📊 图已构建: {len(graph)} 节点, {len(graph.edges)} 边")
    print(f"   起始节点: {graph.start_node}")
    print(f"   终止节点: {[n for n in graph.nodes if graph.is_terminal(n)]}")

    # Validate graph
    print(f"✅ 图验证: {graph.validate_cycles()}")

    # Set up execution
    initial_state = {"prompt": "Explain how neural networks learn from data"}
    state_manager = StateManager(initial_state)
    error_handler = ErrorHandler()

    engine = PregelEngine(graph, state_manager, error_handler)

    print("\n🔄 开始执行...")
    print(f"初始状态: {initial_state}")

    # Execute
    start_time = time.time()
    final_state = engine.execute()
    execution_time = time.time() - start_time

    # Results
    print("\n🎉 执行完成!")
    print(f"总耗时: {execution_time:.2f}s")

    # Display results
    final_data = final_state.to_dict()

    print("\n📋 最终结果:")
    final_output = final_data.get("final_output", {})

    if final_output:
        print(f"   ✨ 最终内容: {final_output.get('summary', 'N/A')}")
        print(f"   🔄 迭代次数: {final_output.get('iterations_needed', 0)}")
        print(f"   🎯 最终得分: {final_output.get('final_score', 0)}")
        print(f"   📊 分支数量: {final_output.get('branches_processed', 0)}")

    print("\n📈 执行统计:")
    stats = engine.get_execution_stats()
    
    # 格式化时间显示
    def format_duration(seconds):
        if seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}分{remaining_seconds:.1f}秒"
    
    def format_timestamp(timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    
    # 显示友好的统计信息
    print(f"   ⏱️  总耗时: {format_duration(stats.get('total_duration', 0))}")
    print(f"   🕐  开始时间: {format_timestamp(stats.get('start_time', 0))}")
    print(f"   🕐  结束时间: {format_timestamp(stats.get('end_time', 0))}")
    print(f"   🔄  超步数量: {stats.get('total_supersteps', 0)}")
    print(f"   ⚙️  执行节点: {stats.get('total_nodes_executed', 0)}")
    print(f"   📨  消息传递: {stats.get('messages_sent', 0)}")
    
    # 显示节点执行时间详情
    node_times = stats.get('node_execution_times', {})
    if node_times:
        print(f"   ⏱️  节点耗时详情:")
        for node_id, duration in node_times.items():
            print(f"      • {node_id}: {format_duration(duration)}")

    return {
        "success": True,
        "final_state": final_data,
        "execution_stats": stats,
        "execution_time": execution_time,
    }


async def run_async_demo():
    """Run async version of the demo."""
    print("\n⚡ 异步综合演示")
    print("=" * 60)

    # Create a simpler async graph for demonstration
    nodes = [
        create_function_node("start", lambda x: {"value": len(x.get("input", "demo"))}),
        create_function_node("double", lambda x: {"value": x["value"] * 2}),
        create_function_node("triple", lambda x: {"value": x["value"] * 3}),
        create_function_node(
            "fan_in", lambda x: {"result": f"Async: {x.get('value', 0)}"}
        ),
    ]

    edges = [
        Edge("start", "double"),
        Edge("start", "triple"),
        Edge("double", "fan_in"),
        Edge("triple", "fan_in"),
    ]

    graph = Graph("async_demo", nodes, edges, "start")

    state_manager = StateManager({"input": "async processing demo"})
    error_handler = ErrorHandler()

    engine = PregelEngine(graph, state_manager, error_handler)

    print("🔄 正在运行异步执行...")
    final_state = await engine.execute_async()

    print("✅ 异步执行完成!")
    print(f"结果: {final_state.to_dict()}")

    return final_state


if __name__ == "__main__":
    # Run comprehensive demo
    result = run_comprehensive_demo()

    # Uncomment to run async demo
    # asyncio.run(run_async_demo())
