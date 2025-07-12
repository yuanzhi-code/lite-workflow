# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Lite Workflow is a modern Chinese-friendly workflow management system inspired by Google Pregel, designed for orchestrating complex AI workflows with elegant graph-based execution patterns.

## Architecture
- **Graph-based**: Clean Node-Edge abstraction with Chinese naming support
- **Pregel-style**: Superstep computation with message passing
- **Modern Python**: Dataclasses, async/await, full type hints
- **Chinese First**: Native Chinese APIs and documentation

## Quick Start

### Environment Setup
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### Running Demos
```bash
# Run comprehensive demo
python demo_chinese.py

# Run standalone demo
python demo_standalone.py

# Run CLI
python -m lite_workflow --demo
```

## Core Structure

### Package Layout
```
src/lite_workflow/
├── definitions/    # Core types (Node, Edge, Graph)
├── core/          # Infrastructure (State, Error, Events)
├── engine/        # Execution engines
├── components/    # LLM integrations
├── cli.py         # Command line interface
└── main.py        # Entry point
```

### Key Components

#### **Workflow Builder** (High-level API)
```python
from lite_workflow import Workflow

workflow = Workflow("中文工作流", {"prompt": "解释AI"})
workflow.chain("处理器A", "处理器B", "处理器C")
result = workflow.run()
```

#### **Graph API** (Low-level API)
```python
from lite_workflow.definitions import Node, Edge, Graph
from lite_workflow.engine import PregelEngine

# Build graph programmatically
graph = Graph("my_graph", nodes, edges, "start_node")
engine = PregelEngine(graph, state_manager, error_handler)
result = engine.execute()
```

## Development Commands

### Setup & Development
```bash
# Install in development mode
uv pip install -e .

# Install development dependencies  
uv pip install -e .[dev]

# Run tests
pytest tests/

# Format code
black src/
ruff check src/

# Type checking
mypy src/
```

### Configuration Files
- `pyproject.toml`: Modern Python packaging
- `requirements.txt`: Generated from pyproject.toml
- No legacy setup.py or requirements.in files

## Key Features

### 1. Modern Design Patterns
- **Fluent interfaces**: `model.bind(temperature=0.9)`
- **Factory functions**: `ChatOpenAI()`, `ChatSiliconFlow()`
- **Type safety**: Full mypy compliance
- **Async support**: Complete async/await throughout

### 2. Chinese-First Design
- Native Chinese APIs and documentation
- Clear Chinese logging messages
- Cultural appropriate terminology
- Extensive Chinese examples

### 3. Demo Files
- `demo_chinese.py`: Full Chinese workflow demo
- `demo_standalone.py`: Self-contained demo
- `examples/`: Usage examples and patterns

## Architecture Quality
- **Clean Architecture**: Separation of concerns
- **Type Safety**: Full type hints and mypy compliance
- **Scalability**: Easy extension with new components
- **Testability**: Modular design for easy testing
- **Performance**: Optimized for both sync and async