# Lite Workflow - AI助手开发指南

> 这是一个给AI助手（如Claude、Cursor AI等）看的项目文档，帮助快速理解项目架构和开发模式。

## 🎯 项目概述

**Lite Workflow** 是一个现代化的中文友好工作流编排系统，灵感来源于 Google Pregel 图计算框架，专为构建复杂的 AI 工作流而设计。

### 核心特性
- **图编排**: 基于节点-边的优雅图结构
- **Pregel 风格**: 超步计算与消息传递
- **并行执行**: 支持扇入/扇出和条件边
- **循环支持**: 迭代改进与质量门控
- **现代 Python**: 类型安全、异步支持、中文友好

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

### 包结构

```
src/lite_workflow/
├── definitions/     # 核心定义
│   ├── node.py      # 节点定义
│   ├── edge.py      # 边定义
│   ├── graph.py     # 图结构
│   ├── state.py     # 状态管理
│   └── message.py   # 消息定义
├── core/           # 基础设施
│   ├── state_manager.py  # 状态管理器
│   ├── error_handler.py  # 错误处理
│   ├── event_bus.py      # 事件总线
│   └── logger.py         # 日志系统
├── engine/         # 执行引擎
│   ├── pregel_engine.py  # Pregel风格引擎
│   ├── execution_engine.py # 抽象执行引擎
│   └── workflow.py       # 高级工作流
├── components/     # 组件实现
│   ├── chat_models.py    # LLM集成
│   ├── function_nodes.py # Python函数节点
│   └── tools.py          # 工具节点（LangChain风格）
└── cli.py          # 命令行接口
```

## 🔧 核心组件详解

### 1. 节点系统 (Node System)

#### 基础节点
```python
from lite_workflow.definitions import Node, NodeConfig

# 创建节点
node = Node(
    node_id="my_node",
    executor=lambda inputs, **context: {"result": "processed"},
    config=NodeConfig()
)
```

#### 函数节点
```python
from lite_workflow.components import PythonFunctionNode, create_function_node

# 方式1: 使用装饰器
@node("data_processor")
def process_data(inputs: dict) -> dict:
    return {"processed": inputs["data"].upper()}

# 方式2: 直接创建
def my_func(inputs: dict) -> dict:
    return {"output": inputs["value"] * 2}

node = create_function_node("multiplier", my_func)
```

### 2. 工具系统 (Tool System) - LangChain风格

#### 工具定义
```python
from lite_workflow import BaseTool, Tool, tool, ToolRegistry

# 方式1: 使用装饰器
@tool(name="calculator", description="执行数学计算")
def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

# 方式2: 继承BaseTool
class SearchTool(BaseTool):
    def __init__(self):
        super().__init__(name="search", description="搜索网络信息")
    
    def _run(self, query: str) -> str:
        return f"搜索结果: 关于'{query}'的信息..."
    
    async def _arun(self, query: str) -> str:
        await asyncio.sleep(0.1)
        return f"异步搜索结果: 关于'{query}'的信息..."
```

#### 工具注册和执行
```python
# 创建注册表
registry = create_tool_registry()

# 注册工具
registry.register_tool(calculate)
registry.register(SearchTool())

# 执行工具
result = registry.execute_tool("calculator", expression="2 + 3 * 4")
async_result = await registry.aexecute_tool("search", query="Python")

# 工具执行器（用于LLM集成）
executor = ToolExecutor(registry)
tool_calls = [
    {
        "id": "call_1",
        "function": {
            "name": "calculator",
            "arguments": '{"expression": "10 + 20"}'
        }
    }
]
results = executor.execute_tool_calls(tool_calls)
```

### 3. LLM集成 (Chat Models)

```python
from lite_workflow.components import OpenAIChatModel, ChatOpenAI

# 基础模型
model = OpenAIChatModel(
    model="gpt-3.5-turbo",
    temperature=0.7
)

# 工厂函数
model = ChatOpenAI(model="gpt-3.5-turbo")

# 使用
result = model.invoke("解释机器学习")
stream = model.stream("写一个Python函数")
```

### 4. 工作流构建 (Workflow Building)

#### 高级API
```python
from lite_workflow import Workflow

# 创建工作流
workflow = Workflow("数据分析", {"data": "原始数据"})

# 添加节点
workflow.add_node("清洗器", lambda x: {"clean": x["data"].strip()})
workflow.add_node("分析器", lambda x: {"result": f"分析: {x['clean']}"})

# 连接节点
workflow.chain("清洗器", "分析器")
# 或者
workflow.add_edge("清洗器", "分析器")

# 执行
result = workflow.run()
```

#### 低级API
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

## 🚀 开发模式

### 1. 节点开发模式

#### 同步节点
```python
def sync_node(inputs: dict, **context) -> dict:
    """同步节点函数"""
    data = inputs.get("data", "")
    processed = data.upper()
    return {"result": processed}
```

#### 异步节点
```python
async def async_node(inputs: dict, **context) -> dict:
    """异步节点函数"""
    data = inputs.get("data", "")
    await asyncio.sleep(0.1)  # 模拟异步操作
    processed = data.upper()
    return {"result": processed}
```

### 2. 工具开发模式

#### 简单工具
```python
@tool(name="simple_tool")
def simple_tool(param: str) -> str:
    return f"处理结果: {param}"
```

#### 复杂工具
```python
class ComplexTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="complex_tool",
            description="复杂工具示例"
        )
    
    def _run(self, **kwargs) -> str:
        # 同步实现
        return "同步结果"
    
    async def _arun(self, **kwargs) -> str:
        # 异步实现
        pass
```

### 3. 高级图模式

#### 扇出模式 (Fan-out)
```python
# 一个节点输出到多个并行节点
edges = [
    Edge("start", "branch_a"),
    Edge("start", "branch_b"),
    Edge("start", "branch_c")
]
```

#### 扇入模式 (Fan-in)
```python
# 多个节点汇聚到一个聚合节点
edges = [
    Edge("branch_a", "aggregator"),
    Edge("branch_b", "aggregator"),
    Edge("branch_c", "aggregator")
]
```

#### 条件边
```python
def condition_function(outputs: dict, state: dict) -> bool:
    return outputs.get("score", 0) > 50

edge = Edge("processor", "next_step", condition=condition_function)
```

#### 循环模式
```python
# 质量门控循环
def quality_gate(inputs: dict) -> dict:
    score = inputs.get("score", 0)
    iteration = inputs.get("iteration", 0)
    
    should_continue = score < 80 and iteration < 3
    return {
        "should_continue": should_continue,
        "iteration": iteration + 1
    }

# 条件边控制循环
edge = Edge("quality_gate", "improver", 
           condition=lambda outputs, state: outputs.get("should_continue", False))
```

## 📝 使用示例

### 基础工作流
```python
from lite_workflow import Workflow

# 创建简单工作流
workflow = Workflow("文本处理", {"text": "Hello World"})

workflow.add_node("大写", lambda x: {"text": x["text"].upper()})
workflow.add_node("反转", lambda x: {"text": x["text"][::-1]})
workflow.add_node("统计", lambda x: {"length": len(x["text"])})

workflow.chain("大写", "反转", "统计")

result = workflow.run()
print(result.final_state.to_dict())
```

### 并行处理
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

### LLM集成工作流
```python
from lite_workflow import Workflow
from lite_workflow.components import ChatOpenAI

# 创建LLM工作流
workflow = Workflow("AI助手", {"question": "什么是机器学习？"})

def call_llm(inputs: dict) -> dict:
    model = ChatOpenAI(model="gpt-3.5-turbo")
    response = model.invoke(inputs["question"])
    return {"answer": response.content}

def format_response(inputs: dict) -> dict:
    answer = inputs["answer"]
    return {"formatted": f"AI回答: {answer}"}

workflow.add_node("llm", call_llm)
workflow.add_node("formatter", format_response)
workflow.chain("llm", "formatter")

result = workflow.run()
```

## 🛠️ 命令行使用

```bash
# 运行演示
python -m lite_workflow --demo

# 运行工作流文件
python -m lite_workflow --workflow path/to/workflow.py

# 详细日志
python -m lite_workflow --demo --verbose
```

## 🔍 关键设计原则

1. **类型安全**: 全面使用类型注解，支持IDE智能提示
2. **异步优先**: 原生支持异步操作，提高并发性能
3. **可扩展性**: 模块化设计，易于添加新组件
4. **中文友好**: 错误信息和日志支持中文
5. **Pregel风格**: 基于超步的图计算模式
6. **LangChain兼容**: 工具系统与LangChain风格一致

## 📚 扩展开发

### 自定义节点类型
```python
class CustomNode(Node):
    def __init__(self, node_id: str, **kwargs):
        super().__init__(node_id, self._execute, **kwargs)
    
    def _execute(self, inputs: dict, **context) -> dict:
        # 自定义执行逻辑
        return {"custom_result": "processed"}
```

### 自定义工具
```python
class CustomTool(BaseTool):
    def _run(self, **kwargs) -> str:
        # 同步实现
        pass
    
    async def _arun(self, **kwargs) -> str:
        # 异步实现
        pass
```

### 自定义执行引擎
```python
class CustomEngine(ExecutionEngine):
    async def execute_async(self) -> State:
        # 自定义执行逻辑
        pass
```

这个框架为构建复杂的AI工作流提供了强大而灵活的基础，特别适合需要并行处理、条件分支和迭代改进的场景。 