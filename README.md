# Lite Workflow

> 现代化的中文友好工作流编排系统 | Modern Chinese-friendly Workflow Orchestration System

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Chinese](https://img.shields.io/badge/中文支持-✓-red.svg)](README.md)

Lite Workflow 是一个现代化的中文友好工作流编排系统，灵感来源于 Google Pregel 图计算框架，专为构建复杂的 AI 工作流而设计。

> **🎯 核心理念**: 让中文开发者能够以直观、模块化和高效的方式构建任何复杂度的 AI 应用。

## ✨ 核心特性

- **🎯 图编排**: 基于节点-边的优雅图结构，支持复杂流程表达
- **⚡ Pregel 风格**: 超步计算与消息传递，高效状态管理
- **🔄 并行执行**: 原生支持扇入/扇出和条件边
- **🔁 循环支持**: 迭代改进与质量门控，完美支持 ReAct 模式
- **📊 现代 Python**: 类型安全、异步优先、中文友好

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
from lite_workflow import Workflow

# 创建简单工作流
workflow = Workflow("我的第一个工作流", {"text": "Hello World"})

# 添加节点
workflow.add_node("大写", lambda x: {"text": x["text"].upper()})
workflow.add_node("反转", lambda x: {"text": x["text"][::-1]})
workflow.add_node("统计", lambda x: {"length": len(x["text"])})

# 连接节点
workflow.chain("大写", "反转", "统计")

# 执行
result = workflow.run()
print(f"结果: {result.final_state.to_dict()}")
# 输出: {'text': 'DLROW OLLEH', 'length': 11}
```

## 🏗️ 架构设计

### 核心概念

#### 1. 图结构 (Node-Edge Graph)
```
节点 (Node) ←→ 边 (Edge) → 节点 (Node)
   ↓               ↑
状态 (State) ← 消息传递 → 状态更新
```

#### 2. Pregel 风格执行
- **超步 (Superstep)**: 每个迭代处理所有活跃节点
- **消息传递**: 节点间通过消息通信，避免共享状态
- **状态同步**: 自动合并并行更新，确保一致性

#### 3. 并行模式
- **扇出 (Fan-out)**: 单节点→多并行处理
- **扇入 (Fan-in)**: 多结果→单聚合器
- **条件边**: 基于结果动态路由

### 包结构

```
src/lite_workflow/
├── definitions/     # 核心定义
│   ├── node.py      # 节点定义和协议
│   ├── edge.py      # 边定义和条件
│   ├── graph.py     # 图结构和验证
│   ├── state.py     # 状态抽象
│   └── message.py   # 消息定义
├── core/           # 基础设施
│   ├── state_manager.py  # 状态管理和冲突解决
│   ├── error_handler.py  # 错误处理和恢复
│   ├── event_bus.py      # 事件总线
│   └── logger.py         # 日志系统
├── engine/         # 执行引擎
│   ├── pregel_engine.py  # Pregel风格引擎
│   ├── execution_engine.py # 抽象执行引擎
│   └── workflow.py       # 高级工作流API
├── components/     # 组件实现
│   ├── chat_models.py    # LLM集成
│   ├── function_nodes.py # Python函数节点
│   └── tools.py          # 工具系统
└── cli.py          # 命令行接口
```

## 📋 使用指南

### 1. 基础工作流

```python
from lite_workflow import Workflow

# 创建工作流
workflow = Workflow("数据分析", {"data": "原始数据"})

# 添加节点
workflow.add_node("清洗器", lambda x: {"clean": x["data"].strip()})
workflow.add_node("分析器", lambda x: {"result": f"分析: {x['clean']}"})

# 连接节点
workflow.chain("清洗器", "分析器")

# 执行
result = workflow.run()
print(result.final_state.to_dict())
```

### 2. 并行处理

```python
from lite_workflow.definitions import Graph, Node, Edge
from lite_workflow.engine import PregelEngine

# 创建并行处理图
nodes = [
    Node("start", lambda x: {"data": x.get("input", "")}),
    Node("branch_a", lambda x: {"result_a": f"A: {x['data']}"}),
    Node("branch_b", lambda x: {"result_b": f"B: {x['data']}"}),
    Node("aggregate", lambda x: {"final": f"{x.get('result_a', '')} + {x.get('result_b', '')}"})
]

edges = [
    Edge("start", "branch_a"),
    Edge("start", "branch_b"),
    Edge("branch_a", "aggregate"),
    Edge("branch_b", "aggregate")
]

graph = Graph("并行处理", nodes, edges, "start")
engine = PregelEngine(graph, {"input": "test data"})
result = engine.execute()
```

### 3. 工具系统

```python
from lite_workflow import tool, create_tool_registry, ToolExecutor

# 使用装饰器创建工具
@tool(name="calculator", description="执行数学计算")
def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

@tool(name="weather", description="获取天气信息")
def get_weather(city: str) -> str:
    weather_data = {
        "北京": "晴天，温度25°C",
        "上海": "多云，温度28°C",
        "广州": "小雨，温度30°C",
    }
    return weather_data.get(city, f"未找到{city}的天气信息")

# 创建工具注册表
registry = create_tool_registry()
registry.register_tool(calculate)
registry.register_tool(get_weather)

# 执行工具
result1 = registry.execute_tool("calculator", expression="2 + 3 * 4")
result2 = registry.execute_tool("weather", city="北京")

print(f"计算: {result1}")
print(f"天气: {result2}")
```

### 4. LLM 集成

```python
from lite_workflow import Workflow
from lite_workflow.components import ChatOpenAI

def call_llm(inputs: dict) -> dict:
    model = ChatOpenAI(model="gpt-3.5-turbo")
    response = model.invoke(inputs["question"])
    return {"answer": response.content}

def format_response(inputs: dict) -> dict:
    answer = inputs["answer"]
    return {"formatted": f"AI回答: {answer}"}

# 创建LLM工作流
workflow = Workflow("AI助手", {"question": "什么是机器学习？"})
workflow.add_node("llm", call_llm)
workflow.add_node("formatter", format_response)
workflow.chain("llm", "formatter")

result = workflow.run()
print(result.final_state.to_dict())
```

### 5. 条件边和循环

```python
from lite_workflow.definitions import Graph, Node, Edge
from lite_workflow.engine import PregelEngine

# 质量门控循环
def quality_gate(inputs: dict) -> dict:
    score = inputs.get("score", 0)
    iteration = inputs.get("iteration", 0)
    
    should_continue = score < 80 and iteration < 3
    return {
        "should_continue": should_continue,
        "iteration": iteration + 1,
        "score": score
    }

def improvement_engine(inputs: dict) -> dict:
    iteration = inputs.get("iteration", 0)
    improved_score = 60 + iteration * 10
    return {
        "score": improved_score,
        "iteration": iteration
    }

# 创建节点
nodes = [
    Node("start", lambda x: {"score": 50, "iteration": 0}),
    Node("quality_gate", quality_gate),
    Node("improvement_engine", improvement_engine),
    Node("final", lambda x: {"final_score": x["score"]})
]

# 创建边（包含循环）
edges = [
    Edge("start", "quality_gate"),
    Edge("quality_gate", "improvement_engine", 
         condition=lambda outputs: outputs.get("should_continue")),
    Edge("improvement_engine", "quality_gate"),
    Edge("quality_gate", "final", 
         condition=lambda outputs: not outputs.get("should_continue"))
]

graph = Graph("质量改进循环", nodes, edges, "start")
engine = PregelEngine(graph, {})
result = engine.execute()
```

## 🎯 高级特性

### 1. 异步支持

```python
import asyncio
from lite_workflow.definitions import Node

# 异步节点
async def async_processor(inputs: dict) -> dict:
    await asyncio.sleep(0.1)  # 模拟异步操作
    return {"processed": inputs["data"].upper()}

# 自动处理同步/异步转换
node = Node("async_processor", async_processor)
```

### 2. 自定义工具

```python
from lite_workflow import BaseTool

class SearchTool(BaseTool):
    def __init__(self):
        super().__init__(name="search", description="搜索网络信息")
    
    def _run(self, query: str) -> str:
        return f"搜索结果: 关于'{query}'的信息..."
    
    async def _arun(self, query: str) -> str:
        await asyncio.sleep(0.1)
        return f"异步搜索结果: 关于'{query}'的信息..."
```

### 3. 状态管理

```python
from lite_workflow.core import StateManager
from lite_workflow.definitions.state import UpdateStrategy

# 创建状态管理器
state_manager = StateManager({"initial": "value"})

# 不同更新策略
state_manager.update({"key1": "value1"}, UpdateStrategy.OVERWRITE)  # 覆盖
state_manager.update({"key2": "value2"}, UpdateStrategy.MERGE)      # 合并
state_manager.update({"key3": "value3"}, UpdateStrategy.IGNORE)     # 忽略已存在
```

## 🛠️ 开发指南

### 环境设置

```bash
# 开发环境
uv pip install -e .[dev]

# 代码格式化
black src/
ruff check src/

# 类型检查
mypy src/

# 运行测试
pytest tests/
```

### 运行演示

```bash
# 运行综合演示
python example/demo_comprehensive.py

# 运行工具演示
python example/demo_tools.py

# 运行CLI演示
python -m lite_workflow --demo
```

### 自定义节点

```python
from lite_workflow.definitions import Node

class CustomNode(Node):
    def __init__(self, node_id: str, **kwargs):
        super().__init__(node_id, self._execute, **kwargs)
    
    def _execute(self, inputs: dict, **context) -> dict:
        # 自定义执行逻辑
        return {"custom_result": "processed"}
```

## 📊 性能特性

- **异步优先**: 原生支持异步操作，提高并发性能
- **并行执行**: 自动并行处理所有活跃节点
- **增量更新**: 只传递状态变化，避免完整状态复制
- **智能合并**: 自动处理字典和列表的合并
- **内存优化**: 消息传递模式减少内存占用

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🌟 致谢

灵感来源于：
- **Google Pregel** 图计算框架
- **LangGraph** 优雅设计模式
- **中国开发者社区** 反馈和建议

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

**Lite Workflow** - 让复杂工作流变得简单而优雅！🚀