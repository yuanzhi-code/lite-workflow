# Lite Workflow

> 轻量级工作流编排系统 | Lightweight Workflow Orchestration System

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Chinese](https://img.shields.io/badge/中文支持-✓-red.svg)](README.md)

Lite Workflow 是一个现代化的工作流编排系统，灵感来源于 Google Pregel 图计算框架，专为构建复杂的 AI 工作流而设计。

> **中文说明**: 支持完整的中文工作流开发体验，包括中文 API、中文日志和中文示例。

## ✨ 特性一览

- **🎯 图编排**: 基于节点-边的优雅图结构
- **⚡ Pregel 风格**: 超步计算与消息传递
- **🇨🇳 中文优先**: 原生中文 API 和文档
- **🔄 并行执行**: 支持扇入/扇出和条件边
- **🔁 循环支持**: 迭代改进与质量门控
- **📊 现代 Python**: 类型安全、异步支持

## 🚀 快速开始

### 环境准备

```bash
# 安装 UV（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv
source .venv/bin/activate

# 安装项目
uv pip install -e .
```

### 30 秒上手

```python
# 简单工作流
from lite_workflow import Workflow

workflow = Workflow("我的第一个工作流", {"prompt": "解释机器学习"})
workflow.chain("处理器A", "处理器B", "处理器C")
result = workflow.run()

print(f"结果: {result.final_state}")
```

### 中文工作流示例

```python
from lite_workflow import Workflow
from lite_workflow.components.function_nodes import node

@node("数据处理器")
def 处理数据(inputs: dict) -> dict:
    return {"处理结果": inputs["prompt"].upper()}

@node("AI生成器")
def 生成内容(inputs: dict) -> dict:
    from lite_workflow.components.chat_models import ChatOpenAI
    model = ChatOpenAI(model="gpt-3.5-turbo")
    result = model.invoke(inputs["处理结果"])
    return {"内容": result.content}

# 构建中文工作流
workflow = Workflow("中文AI工作流", {"prompt": "什么是深度学习？"})
workflow.chain("数据处理器", "AI生成器")
result = workflow.run()
print(result.final_state["内容"])
```

## 🏗️ 架构设计

### 核心概念

#### 1. 图结构 (Graph)
```
节点 (Node) ←→ 边 (Edge) → 节点 (Node)
   ↓               ↑
状态 (State) ← 消息传递 → 状态更新
```

#### 2. 执行模式
- **超步 (Superstep)**: 每个迭代处理所有活跃节点
- **消息传递**: 节点间通过消息通信
- **状态同步**: 自动合并并行更新

#### 3. 并行模式
- **扇出 (Fan-out)**: 单节点→多并行处理
- **扇入 (Fan-in)**: 多结果→单聚合器
- **条件边**: 基于结果动态路由

### 包结构

```
lite_workflow/
├── definitions/     # 核心定义
│   ├── node.py      # 节点定义
│   ├── edge.py      # 边定义
│   ├── graph.py     # 图结构
│   └── state.py     # 状态管理
├── core/           # 基础设施
│   ├── state_manager.py  # 状态管理器
│   ├── error_handler.py  # 错误处理
│   └── event_bus.py      # 事件总线
├── engine/         # 执行引擎
│   ├── pregel_engine.py  # Pregel风格引擎
│   └── workflow.py       # 高级工作流
├── components/     # 组件实现
│   ├── chat_models.py    # LLM集成
│   ├── function_nodes.py # Python函数节点
│   └── tools.py          # 工具节点
└── cli.py          # 命令行接口
```

## 📋 使用指南

### 基础工作流

```python
from lite_workflow import Workflow

# 创建工作流
workflow = Workflow("数据分析", {"data": "原始数据"})

# 添加节点
workflow.add_node("清洗器", lambda x: {"clean": x["data"].strip()})
workflow.add_node("分析器", lambda x: {"result": f"分析: {x['clean']}"})

# 连接节点
workflow.add_edge("清洗器", "分析器")
workflow.set_start_node("清洗器")

# 执行
result = workflow.run()
print(result.final_state["result"])
```

### 高级图编排

```python
from lite_workflow.definitions import Node, Edge, Graph
from lite_workflow.engine import PregelEngine

# 创建节点
nodes = [
    Node("start", lambda x: {"value": 1}),
    Node("double", lambda x: {"value": x["value"] * 2}),
    Node("triple", lambda x: {"value": x["value"] * 3}),
    Node("aggregate", lambda x: {"result": x["value"]})
]

# 创建边
edges = [
    Edge("start", "double"),
    Edge("start", "triple"),
    Edge("double", "aggregate"),
    Edge("triple", "aggregate")
]

# 构建图
graph = Graph("并行处理", nodes, edges, "start")
engine = PregelEngine(graph, {"value": 10})
result = engine.execute()
```

### 中文演示

```bash
# 运行中文演示
python demo_chinese.py

# 运行独立演示
python demo_standalone.py
```

## 🎯 高级特性

### 1. 条件边
```python
from lite_workflow.definitions.edge import when

# 条件路由
edge = Edge("decision", "high_path", condition=lambda outputs: outputs["score"] > 80)
```

### 2. 循环改进
```python
# 质量门控循环
workflow.add_edge("quality_check", "improver", 
                 condition=lambda x: x["quality"] < 90)
workflow.add_edge("improver", "quality_check")
```

### 3. 异步支持
```python
from lite_workflow.engine import PregelEngine

engine = PregelEngine(graph, state_manager, error_handler)
result = await engine.execute_async()
```

## 🛠️ 开发指南

### 环境设置
```bash
# 开发环境
uv pip install -e .[dev]

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/

# 代码检查
ruff check src/
```

### 测试运行
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_engine.py -v
```

## 📚 示例和教程

### 目录结构
- `demo_chinese.py`: 中文工作流演示
- `demo_standalone.py`: 独立图编排演示
- `examples/`: 使用示例和最佳实践

### 学习路径
1. **新手**: 从 `demo_chinese.py` 开始
2. **进阶**: 使用 `Workflow` 类构建复杂流程
3. **专家**: 直接操作 `PregelEngine` 进行低级控制

## 🔧 集成示例

### OpenAI 集成
```python
from lite_workflow.components import ChatOpenAI, ChatSiliconFlow

# 使用 OpenAI
model = ChatOpenAI(model="gpt-4")

# 使用 SiliconFlow（中文模型）
siliconflow = ChatSiliconFlow(model="Qwen/Qwen3-8B")
```

### 自定义节点
```python
from lite_workflow.components.function_nodes import node

@node("我的处理器")
def 自定义处理(inputs: dict) -> dict:
    return {"处理结果": inputs["数据"] * 2}
```

## 📊 性能特点

- **并行执行**: 自动并行处理独立节点
- **状态优化**: 增量更新，避免全状态复制
- **错误恢复**: 节点级错误处理和重试
- **内存高效**: 智能状态合并策略

## 🤝 贡献指南

我们欢迎贡献！请查看：
- [贡献指南](CONTRIBUTING.md)
- [开发文档](docs/development.md)
- [API文档](docs/api.md)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🌟 致谢

灵感来源于：
- Google Pregel 图计算框架
- LangChain 优雅设计模式
- 中国开发者社区反馈

---

**Lite Workflow** - 让复杂工作流变得简单而优雅！