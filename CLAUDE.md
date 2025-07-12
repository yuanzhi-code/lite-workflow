# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a lightweight workflow management system inspired by Google Pregel, designed for orchestrating complex LLM applications using graph-based execution. The system supports fan-out/fan-in patterns, conditional edges, loops, and incremental state management.

## Architecture
- **Graph-based**: Uses Node-Edge abstraction where nodes are computation units and edges define data/control flow
- **Pregel-style**: Incremental state updates via message passing between supersteps
- **Modular**: Clean separation between definitions, execution, and components

## Key Components

### Core Structure
- `definitions/`: Data structures and interfaces
  - `graph.py`: Node, Edge, Graph classes
  - `state.py`: State management and IncrementalUpdate
  - `chat_models.py`: BaseChatModel and Message abstractions
- `engine/`: Execution logic
  - `execution_engine.py`: Pregel-style superstep execution
- `core/`: Supporting systems
  - `state_manager.py`: Global state coordination
  - `error_handler.py`: Node-level error handling
- `components/`: Concrete implementations
  - `openai_chat_model.py`: OpenAI-compatible chat model integration

### Execution Model
1. **Superstep-based**: Each iteration processes all active nodes
2. **Message passing**: Nodes receive inputs via messages, return incremental updates
3. **State merging**: Automatic conflict resolution for parallel updates
4. **Conditional edges**: Dynamic routing based on node outputs

## Development Commands

### Setup
```bash
# Install uv if not available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### Running
```bash
# Execute main workflow
python main.py

# The main.py demonstrates:
# - Graph construction with fan-out/fan-in/loops
# - LLM integration via OpenAIChatModel
# - Conditional edge routing
# - Iterative processing
```

### Key Files for Development
- `main.py`: Complete workflow example and integration test
- `execution_engine.py`: Core execution logic (superstep algorithm)
- `graph.py`: Node execution and edge traversal
- `state_manager.py`: State update and conflict resolution

### Development Patterns
- **Node creation**: Extend Node class with custom `function_ref` in config
- **LLM integration**: Use OpenAIChatModel or implement BaseChatModel
- **State updates**: Return dict from node functions for incremental updates
- **Conditional logic**: Use Edge.condition with output.key or state.key expressions
- **Error handling**: Register callbacks via ErrorHandler for node-specific handling

### Current Limitations
- Sequential node execution (parallel execution TODO)
- Simple string-based condition evaluation (unsafe for production)
- No persistence or recovery mechanisms
- Basic error handling without retry logic