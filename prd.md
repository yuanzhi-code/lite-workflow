# Lite Workflow 设计文档

## 1. 项目概述

### 1.1 项目背景与目标

Lite Workflow 是一个现代化的中文友好工作流编排系统，灵感来源于 Google Pregel 图计算框架，专为构建复杂的 AI 工作流而设计。

**核心目标：**
- 提供基于图结构的优雅工作流编排
- 支持复杂的并行处理、条件分支和迭代推理
- 原生中文友好，降低中文开发者使用门槛
- 现代化 Python 技术栈，类型安全、异步优先

### 1.2 产品愿景

成为中文 AI 开发者的首选工作流编排框架，使开发者能够以直观、模块化和高效的方式构建任何复杂度的 AI 应用。

## 2. 核心架构设计

### 2.1 图结构抽象 (Node-Edge Graph)

#### 核心概念
- **Node（节点）**: 独立的计算单元，可以是 LLM 调用、工具执行、自定义函数
- **Edge（边）**: 数据流和控制流的方向，支持条件路由
- **Graph（图）**: 节点和边的集合，定义完整的工作流结构

#### 架构优势
```python
# 顺序执行
workflow.chain("步骤1", "步骤2", "步骤3")

# 并行执行 (Fan-out)
workflow.add_edge("开始", "分支A")
workflow.add_edge("开始", "分支B")

# 条件分支
edge = Edge("判断", "分支A", condition=lambda outputs: outputs.get("score") > 50)

# 循环迭代
edge = Edge("质量门", "改进器", condition=lambda outputs: outputs.get("should_continue"))
```

### 2.2 Pregel 风格执行引擎

#### 超步计算 (Superstep)
- **消息传递**: 节点间通过消息通信，而非共享状态
- **状态同步**: 自动合并并行更新，确保一致性
- **增量更新**: 只传递状态变化，避免完整状态复制

#### 执行流程
```
超步 0: 初始化 → 活跃节点 [开始]
超步 1: 执行开始节点 → 发送消息到 [分支A, 分支B]
超步 2: 并行执行分支 → 发送消息到 [聚合器]
超步 3: 执行聚合器 → 发送消息到 [质量门]
超步 4: 条件判断 → 决定是否继续循环
```

### 2.3 现代化技术栈

#### 类型安全
```python
from typing import Any, Callable
from typing_extensions import TypeAlias

NodeId: TypeAlias = str
NodeFunction: TypeAlias = Callable[..., dict[str, Any]]
```

#### 异步优先
```python
async def async_node(inputs: dict, **context) -> dict:
    await asyncio.sleep(0.1)
    return {"result": "processed"}

# 自动处理同步/异步转换
node = Node("async_node", async_node)
```

#### 中文友好
```python
# 支持中文节点名和错误信息
workflow = Workflow("数据分析工作流", {"数据": "原始数据"})
workflow.add_node("数据清洗器", clean_data)
workflow.add_node("结果分析器", analyze_results)
```

## 3. 核心组件设计

### 3.1 包结构设计

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

### 3.2 核心组件详解

#### 节点系统 (Node System)
```python
@dataclass
class NodeConfig:
    timeout: float | None = None
    retry_count: int = 0
    retry_delay: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

class Node:
    def __init__(self, node_id: NodeId, executor: NodeExecutor, config: NodeConfig | None = None):
        self.node_id = node_id
        self.executor = executor
        self.config = config or NodeConfig()
    
    async def execute_async(self, inputs: dict, **context) -> dict:
        # 自动处理同步/异步执行器
        if asyncio.iscoroutinefunction(self.executor):
            return await self.executor(inputs, **context)
        else:
            return await asyncio.to_thread(self.executor, inputs, **context)
```

#### 状态管理系统 (State Management)
```python
class StateManager:
    def __init__(self, initial_state: dict | None = None):
        self._state = InMemoryState(initial_state)
        self._lock = threading.RLock()
        self._merge_strategies: dict[str, MergeStrategy] = {}
    
    def update(self, updates: dict, strategy: UpdateStrategy = UpdateStrategy.OVERWRITE):
        # 支持多种更新策略：覆盖、合并、忽略、抛出异常
        with self._lock:
            for key, new_value in updates.items():
                if strategy == UpdateStrategy.MERGE:
                    self._merge_value(key, new_value)
                else:
                    self.set(key, new_value)
```

#### 工具系统 (Tool System)
```python
# 装饰器方式
@tool(name="calculator", description="执行数学计算")
def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

# 类继承方式
class SearchTool(BaseTool):
    def __init__(self):
        super().__init__(name="search", description="搜索网络信息")
    
    def _run(self, query: str) -> str:
        return f"搜索结果: 关于'{query}'的信息..."
    
    async def _arun(self, query: str) -> str:
        await asyncio.sleep(0.1)
        return f"异步搜索结果: 关于'{query}'的信息..."

# 工具注册和执行
registry = create_tool_registry()
registry.register_tool(calculate)
registry.register(SearchTool())

result = registry.execute_tool("calculator", expression="2 + 3 * 4")
```

### 3.3 执行引擎设计

#### Pregel 引擎核心逻辑
```python
class PregelEngine(ExecutionEngine):
    async def execute_async(self) -> State:
        current_messages = self._initialize_messages()
        superstep = 0
        
        while superstep < self.config.max_iterations:
            if not any(current_messages.values()):
                break
            
            # 执行超步
            new_messages = await self._execute_superstep_async(current_messages, superstep)
            current_messages = new_messages
            superstep += 1
        
        return self.state_manager.get_state()
    
    async def _execute_superstep_async(self, messages: dict, superstep: int):
        # 1. 识别活跃节点
        active_nodes = [node_id for node_id, msgs in messages.items() if msgs]
        
        # 2. 并行执行所有活跃节点
        tasks = [self._execute_node_async(node_id, messages[node_id], superstep) 
                for node_id in active_nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. 收集新消息
        new_messages = defaultdict(list)
        for node_id, result in zip(active_nodes, results):
            if isinstance(result, Exception):
                # 错误处理
                continue
            
            # 发送消息到邻居节点
            outgoing_edges = self.graph.get_outgoing_edges(node_id)
            for edge in outgoing_edges:
                if edge.should_traverse(result, self.state_manager.get_state()):
                    new_messages[edge.target_id].append(result)
        
        return new_messages
```

## 4. 高级功能设计

### 4.1 并行处理模式

#### Fan-out (扇出)
```python
# 一个节点输出到多个并行节点
edges = [
    Edge("start", "branch_a"),
    Edge("start", "branch_b"), 
    Edge("start", "branch_c")
]

# 执行时自动并行处理
# 超步 1: start → [branch_a, branch_b, branch_c] (并行)
# 超步 2: [branch_a, branch_b, branch_c] → aggregator (等待所有完成)
```

#### Fan-in (扇入)
```python
# 多个节点汇聚到一个聚合节点
edges = [
    Edge("branch_a", "aggregator"),
    Edge("branch_b", "aggregator"),
    Edge("branch_c", "aggregator")
]

# 状态管理器自动合并多个输入
def aggregator(inputs: dict) -> dict:
    # inputs 包含所有上游节点的输出
    return {"aggregated": sum(inputs.values())}
```

### 4.2 条件边和动态路由

```python
def quality_gate(inputs: dict) -> dict:
    score = inputs.get("score", 0)
    return {
        "should_continue": score < 80,
        "score": score
    }

# 条件边
edge = Edge("quality_gate", "improver", 
           condition=lambda outputs, state: outputs.get("should_continue", False))

# 条件边实现
def should_traverse(self, outputs: dict, state: dict) -> bool:
    if self.condition is None:
        return True
    return self.condition(outputs, state)
```

### 4.3 循环和迭代

```python
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
    # 模拟改进过程
    improved_score = 60 + iteration * 10
    return {
        "score": improved_score,
        "iteration": iteration
    }

# 循环边
edges = [
    Edge("quality_gate", "improvement_engine", 
         condition=lambda outputs: outputs.get("should_continue")),
    Edge("improvement_engine", "quality_gate")
]
```

## 5. 使用模式设计

### 5.1 高级 API (Workflow)

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

### 5.2 低级 API (Graph + Engine)

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

### 5.3 LLM 集成模式

```python
from lite_workflow.components import ChatOpenAI

def call_llm(inputs: dict) -> dict:
    model = ChatOpenAI(model="gpt-3.5-turbo")
    response = model.invoke(inputs["question"])
    return {"answer": response.content}

def format_response(inputs: dict) -> dict:
    answer = inputs["answer"]
    return {"formatted": f"AI回答: {answer}"}

workflow = Workflow("AI助手", {"question": "什么是机器学习？"})
workflow.add_node("llm", call_llm)
workflow.add_node("formatter", format_response)
workflow.chain("llm", "formatter")

result = workflow.run()
```

## 6. 扩展性设计

### 6.1 自定义节点类型

```python
class CustomNode(Node):
    def __init__(self, node_id: str, **kwargs):
        super().__init__(node_id, self._execute, **kwargs)
    
    def _execute(self, inputs: dict, **context) -> dict:
        # 自定义执行逻辑
        return {"custom_result": "processed"}
```

### 6.2 自定义工具

```python
class CustomTool(BaseTool):
    def _run(self, **kwargs) -> str:
        # 同步实现
        return "同步结果"
    
    async def _arun(self, **kwargs) -> str:
        # 异步实现
        return "异步结果"
```

### 6.3 自定义执行引擎

```python
class CustomEngine(ExecutionEngine):
    async def execute_async(self) -> State:
        # 自定义执行逻辑
        pass
```

## 7. 性能优化设计

### 7.1 异步执行

- **节点级别**: 自动检测同步/异步函数，使用 `asyncio.to_thread` 处理同步函数
- **图级别**: 并行执行所有活跃节点
- **工具级别**: 支持同步和异步工具调用

### 7.2 状态管理优化

- **增量更新**: 只传递状态变化，避免完整状态复制
- **智能合并**: 自动处理字典和列表的合并
- **线程安全**: 使用 RLock 确保并发安全

### 7.3 内存管理

- **消息传递**: 避免共享状态，减少内存占用
- **状态快照**: 支持状态快照和恢复
- **垃圾回收**: 及时清理过期的消息和状态

## 8. 错误处理设计

### 8.1 分层错误处理

```python
class ErrorHandler:
    async def handle_error_async(self, node_id: str, error: Exception, context: dict):
        # 1. 记录错误
        self.logger.error(f"Node {node_id} failed: {error}")
        
        # 2. 尝试恢复
        if self.retry_count < self.max_retries:
            return await self._retry_node(node_id, context)
        
        # 3. 降级处理
        return await self._fallback_processing(node_id, error, context)
```

### 8.2 错误恢复策略

- **重试机制**: 支持指数退避重试
- **降级处理**: 提供默认值或简化处理
- **错误传播**: 向上层传播不可恢复的错误

## 9. 监控和日志设计

### 9.1 事件总线

```python
class EventBus:
    def emit(self, event: Event):
        # 发布事件到所有监听器
        for listener in self._listeners:
            listener(event)

# 事件类型
class SuperStepEvent(Event):
    def __init__(self, superstep: int, active_nodes: list, completed_nodes: list):
        super().__init__("superstep", {
            "superstep": superstep,
            "active_nodes": active_nodes,
            "completed_nodes": completed_nodes
        })
```

### 9.2 日志系统

```python
class Logger:
    def log_workflow_start(self, graph_id: str):
        self.info(f"🚀 工作流 {graph_id} 开始执行")
    
    def log_workflow_complete(self, graph_id: str, duration: float, final_state: dict):
        self.info(f"✅ 工作流 {graph_id} 完成，耗时 {duration:.2f}s")
```

## 10. 部署和配置

### 10.1 环境配置

```python
# 支持环境变量配置
import os
model = OpenAIChatModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
```

### 10.2 命令行工具

```bash
# 运行演示
python -m lite_workflow --demo

# 运行工作流文件
python -m lite_workflow --workflow path/to/workflow.py

# 详细日志
python -m lite_workflow --demo --verbose
```

## 11. 未来扩展计划

### 11.1 短期目标 (MVP后)

- **持久化**: 支持工作流状态持久化到数据库
- **可视化**: 提供图执行过程的可视化界面
- **监控**: 添加性能监控和指标收集
- **版本控制**: 支持工作流定义的版本管理

### 11.2 长期目标

- **分布式执行**: 支持跨机器的分布式工作流执行
- **实时流处理**: 支持实时数据流处理
- **机器学习集成**: 深度集成 ML 框架
- **云原生**: 支持 Kubernetes 部署

---

这个设计文档基于实际实现，提供了完整的架构指导，确保系统的可扩展性、可维护性和高性能。