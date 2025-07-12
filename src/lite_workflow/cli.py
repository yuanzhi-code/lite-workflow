"""
Command-line interface for Lite Workflow.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from .engine.workflow import Workflow


def create_demo_workflow() -> Workflow:
    """Create a demonstration workflow."""
    from .components.function_nodes import node
    from .components.chat_models import ChatOpenAI
    
    @node("data_processor")
    def process_data(inputs: dict) -> dict:
        """Process input data."""
        prompt = inputs.get("prompt", "")
        return {"processed_prompt": prompt.upper()}
    
    @node("llm_caller")
    def call_llm(inputs: dict) -> dict:
        """Call LLM with processed data."""
        prompt = inputs.get("processed_prompt", "")
        model = ChatOpenAI(model="gpt-3.5-turbo")
        result = model.invoke(prompt)
        return {"llm_response": result.content}
    
    @node("final_processor")
    def finalize(inputs: dict) -> dict:
        """Final processing."""
        response = inputs.get("llm_response", "")
        return {"final_result": f"Workflow result: {response}"}
    
    # Build workflow
    workflow = Workflow("demo_workflow", {"prompt": "Hello, workflow!"})
    workflow.chain("data_processor", "llm_caller", "final_processor")
    
    return workflow


def run_demo():
    """Run the demonstration workflow."""
    workflow = create_demo_workflow()
    result = workflow.run()
    
    print("=== Workflow Demo ===")
    print(f"Success: {result.success}")
    print(f"Final Result: {result.final_state.to_dict().get('final_result', 'N/A')}")
    print(f"Execution Stats: {result.execution_stats}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Lite Workflow CLI")
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Run demonstration workflow"
    )
    parser.add_argument(
        "--workflow", 
        type=str, 
        help="Path to workflow file"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.workflow:
        # TODO: Load and execute workflow from file
        print("Loading workflow from file...")
    else:
        run_demo()


if __name__ == "__main__":
    main()