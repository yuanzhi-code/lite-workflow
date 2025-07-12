#!/usr/bin/env python3
"""
Standalone Graph Demo - Fan-in/Fan-out, Conditional Edges, Loops

This standalone demo runs without installation to test the graph structure.
"""

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict


# 🎯 Simple implementations for demo

@dataclass
class Node:
    node_id: str
    executor: callable

@dataclass  
class Edge:
    source_id: str
    target_id: str
    condition: Optional[callable] = None
    
    def should_traverse(self, outputs: Dict[str, Any], state: Dict[str, Any]) -> bool:
        if self.condition is None:
            return True
        return self.condition(outputs, state)


class SimpleGraph:
    """Simple graph implementation for demo."""
    
    def __init__(self, graph_id: str, nodes: List[Node], edges: List[Edge], start_node: str):
        self.graph_id = graph_id
        self.nodes = {node.node_id: node for node in nodes}
        self.edges = edges
        self.start_node = start_node
        
        # Build adjacency lists
        self._out_edges = defaultdict(list)
        self._in_edges = defaultdict(list)
        for edge in edges:
            self._out_edges[edge.source_id].append(edge)
            self._in_edges[edge.target_id].append(edge)
    
    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        return self._out_edges.get(node_id, [])


class SimpleEngine:
    """Simple Pregel-style execution engine."""
    
    def __init__(self, graph: SimpleGraph, initial_state: Dict[str, Any]):
        self.graph = graph
        self.state = initial_state.copy()
        self.execution_stats = {
            "supersteps": 0,
            "nodes_executed": 0,
            "messages_sent": 0
        }
    
    def execute(self) -> Dict[str, Any]:
        """Execute the graph with supersteps."""
        print(f"🚀 Starting {self.graph.graph_id}")
        
        # Initialize messages
        messages = defaultdict(list)
        messages[self.graph.start_node].append(self.state)
        
        superstep = 0
        
        while superstep < 100:  # Max iterations
            active_nodes = [n for n, msgs in messages.items() if msgs]
            
            if not active_nodes:
                break
                
            print(f"\n📊 Superstep {superstep}: Active nodes {active_nodes}")
            
            new_messages = defaultdict(list)
            
            for node_id in active_nodes:
                node = self.graph.nodes[node_id]
                
                # Aggregate inputs
                aggregated = {}
                for msg in messages[node_id]:
                    aggregated.update(msg)
                
                # Execute node
                print(f"⚙️  Executing {node_id}")
                outputs = node.executor(aggregated)
                self.execution_stats["nodes_executed"] += 1
                
                # Update state
                self.state.update(outputs)
                
                # Send messages to neighbors
                for edge in self.graph.get_outgoing_edges(node_id):
                    if edge.should_traverse(outputs, self.state):
                        new_messages[edge.target_id].append(outputs)
                        self.execution_stats["messages_sent"] += 1
                        print(f"   📨 Message to {edge.target_id}")
            
            messages = new_messages
            superstep += 1
            self.execution_stats["supersteps"] = superstep
        
        return self.state


# 🎯 Node Functions

def initial_processor(inputs: dict) -> dict:
    """Process initial input and fan-out."""
    prompt = inputs.get("prompt", "Test prompt")
    print(f"📝 Processing: {prompt}")
    return {
        "original_prompt": prompt,
        "processed_prompt": prompt.upper(),
        "fan_out_ready": True
    }


def processor_a(inputs: dict) -> dict:
    """First parallel processor."""
    prompt = inputs.get("processed_prompt", "")
    print(f"🔍 [A] Branch A processing: {prompt[:20]}...")
    return {
        "branch_a_result": f"A: {len(prompt)} chars",
        "a_score": len(prompt)
    }


def processor_b(inputs: dict) -> dict:
    """Second parallel processor."""
    prompt = inputs.get("processed_prompt", "")
    print(f"⚡ [B] Branch B processing: {prompt[:20]}...")
    return {
        "branch_b_result": f"B: {prompt[:10]}...",
        "b_score": len(prompt) * 2
    }


def processor_c(inputs: dict) -> dict:
    """Third parallel processor."""
    prompt = inputs.get("processed_prompt", "")
    print(f"🎨 [C] Branch C processing: {prompt[:20]}...")
    return {
        "branch_c_result": f"C: {prompt[-10:]}...",
        "c_score": len(prompt) * 3
    }


def aggregator(inputs: dict) -> dict:
    """Fan-in aggregation."""
    print(f"🎯 [FAN-IN] Aggregating results")
    
    all_scores = {
        "a": inputs.get("a_score", 0),
        "b": inputs.get("b_score", 0),
        "c": inputs.get("c_score", 0)
    }
    
    total_score = sum(all_scores.values())
    
    return {
        "aggregated_results": {
            "branches": [inputs.get("branch_a_result"), inputs.get("branch_b_result"), inputs.get("branch_c_result")],
            "scores": all_scores,
            "total_score": total_score
        },
        "iteration": inputs.get("iteration", 0),
        "continue_processing": total_score < 100
    }


def loop_condition(inputs: dict) -> dict:
    """Check if we should continue looping."""
    iteration = inputs.get("iteration", 0)
    should_continue = inputs.get("continue_processing", False)
    
    print(f"🔄 [LOOP CHECK] Iteration {iteration}, Continue: {should_continue}")
    
    return {
        "iteration": iteration,
        "should_continue": should_continue,
        "final_iteration": iteration
    }


def loop_improver(inputs: dict) -> dict:
    """Improve results for next iteration."""
    iteration = inputs.get("iteration", 0)
    
    print(f"🔧 [IMPROVEMENT] Enhancing iteration {iteration}")
    
    return {
        "processed_prompt": f"ENHANCED_{iteration}",
        "iteration": iteration + 1,
        "improvement_factor": iteration + 1
    }


def final_processor(inputs: dict) -> dict:
    """Final processing when complete."""
    iteration = inputs.get("iteration", 0)
    aggregated = inputs.get("aggregated_results", {})
    
    print(f"🎉 [FINAL] Processing complete after {iteration} iterations")
    
    return {
        "final_result": {
            "summary": f"Completed after {iteration} iterations",
            "branches_processed": len(aggregated.get("branches", [])),
            "final_score": aggregated.get("total_score", 0),
            "quality_achieved": True
        },
        "process_complete": True
    }


# 🏗️ Graph Construction

def create_demo_graph() -> SimpleGraph:
    """Create demo graph with all patterns."""
    
    nodes = [
        Node("initial_processor", initial_processor),
        Node("processor_a", processor_a),
        Node("processor_b", processor_b),
        Node("processor_c", processor_c),
        Node("aggregator", aggregator),
        Node("loop_condition", loop_condition),
        Node("loop_improver", loop_improver),
        Node("final_processor", final_processor)
    ]
    
    edges = [
        # Initial processing
        Edge("initial_processor", "processor_a"),
        Edge("initial_processor", "processor_b"),
        Edge("initial_processor", "processor_c"),
        
        # Fan-in aggregation
        Edge("processor_a", "aggregator"),
        Edge("processor_b", "aggregator"),
        Edge("processor_c", "aggregator"),
        
        # Quality check
        Edge("aggregator", "loop_condition"),
        
        # Loop back for improvement
        Edge("loop_condition", "loop_improver", 
             condition=lambda outputs, state: outputs.get("should_continue", False)),
        Edge("loop_improver", "processor_a"),
        Edge("loop_improver", "processor_b"),
        Edge("loop_improver", "processor_c"),
        
        # Final processing
        Edge("loop_condition", "final_processor", 
             condition=lambda outputs, state: not outputs.get("should_continue", False))
    ]
    
    return SimpleGraph("comprehensive_demo", nodes, edges, "initial_processor")


# 🚀 Demo Execution

def run_graph_demo():
    """Run the comprehensive graph demo."""
    print("🎯 COMPREHENSIVE GRAPH DEMO")
    print("=" * 60)
    print("📊 Features:")
    print("   ✅ Fan-out: single → multiple parallel processors")
    print("   ✅ Fan-in: multiple results → single aggregator")
    print("   ✅ Conditional edges: loop based on quality")
    print("   ✅ State management: iteration tracking")
    print("   ✅ Message passing: data flow between nodes")
    print()
    
    # Create and run graph
    graph = create_demo_graph()
    engine = SimpleEngine(graph, {"prompt": "Explain machine learning"})
    
    print("🔄 Starting execution...")
    start_time = time.time()
    
    final_state = engine.execute()
    
    execution_time = time.time() - start_time
    
    print(f"\n🎉 Execution Complete!")
    print(f"⏱️  Total time: {execution_time:.2f}s")
    print(f"📊 Supersteps: {engine.execution_stats['supersteps']}")
    print(f"⚙️  Nodes executed: {engine.execution_stats['nodes_executed']}")
    print(f"📨 Messages sent: {engine.execution_stats['messages_sent']}")
    
    print(f"\n📋 Final Results:")
    final_result = final_state.get("final_result", {})
    
    if final_result:
        print(f"   🎯 Summary: {final_result.get('summary', 'N/A')}")
        print(f"   📊 Final Score: {final_result.get('final_score', 0)}")
        print(f"   🔄 Iterations: {final_result.get('branches_processed', 0)}")
    
    # Show all data
    print(f"\n🔍 Complete State:")
    for key, value in final_state.items():
        if key != "branches":  # Skip long branch content
            print(f"   {key}: {value}")
    
    return final_state


if __name__ == "__main__":
    result = run_graph_demo()