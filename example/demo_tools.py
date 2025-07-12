"""
演示新的工具系统功能

展示如何使用重构后的工具系统，包括工具定义、注册、执行等。
"""

import asyncio

from lite_workflow import (
    BaseTool,
    ToolExecutor,
    ToolNode,
    Workflow,
    create_tool_registry,
    tool,
)


# 1. 使用装饰器创建工具
@tool(name="calculator", description="执行数学计算")
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@tool(name="weather", description="获取天气信息")
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 模拟天气API调用
    weather_data = {
        "北京": "晴天，温度25°C",
        "上海": "多云，温度28°C",
        "广州": "小雨，温度30°C",
    }
    return weather_data.get(city, f"未找到{city}的天气信息")


# 2. 创建自定义工具类
class SearchTool(BaseTool):
    """搜索工具示例"""

    def __init__(self):
        super().__init__(name="search", description="搜索网络信息")

    def _run(self, query: str) -> str:
        """执行搜索"""
        # 模拟搜索功能
        return f"搜索结果: 关于'{query}'的信息..."

    async def _arun(self, query: str) -> str:
        """异步执行搜索"""
        # 模拟异步搜索
        await asyncio.sleep(0.1)
        return f"异步搜索结果: 关于'{query}'的信息..."


# 3. 异步工具示例
@tool(name="async_processor", description="异步处理数据")
async def async_process_data(data: str) -> str:
    """异步处理数据"""
    await asyncio.sleep(0.5)  # 模拟异步处理
    return f"处理完成: {data.upper()}"


def demo_basic_tools():
    """演示基础工具功能"""
    print("=== 基础工具演示 ===")

    # 创建工具注册表
    registry = create_tool_registry()

    # 注册工具（直接注册装饰后的对象，不要再传name）
    registry.register_tool(calculate)
    registry.register_tool(get_weather)

    # 创建自定义工具
    search_tool = SearchTool()
    registry.register(search_tool)

    # 列出所有工具
    print(f"注册的工具: {registry.list_tools()}")

    # 执行工具（名称与装饰器一致）
    result1 = registry.execute_tool("calculator", expression="2 + 3 * 4")
    result2 = registry.execute_tool("weather", city="北京")
    result3 = registry.execute_tool("search", query="Python编程")

    print(f"计算结果: {result1}")
    print(f"天气信息: {result2}")
    print(f"搜索结果: {result3}")

    # 获取OpenAI格式的工具定义
    openai_tools = registry.get_tools_for_openai()
    print(f"OpenAI格式工具定义: {len(openai_tools)} 个工具")


async def demo_async_tools():
    """演示异步工具功能"""
    print("\n=== 异步工具演示 ===")

    registry = create_tool_registry()
    registry.register_tool(async_process_data)

    # 异步执行工具
    result = await registry.aexecute_tool("async_processor", data="hello world")
    print(f"异步处理结果: {result}")


def demo_tool_executor():
    """演示工具执行器"""
    print("\n=== 工具执行器演示 ===")

    registry = create_tool_registry()
    registry.register_tool(calculate)
    registry.register_tool(get_weather)

    executor = ToolExecutor(registry)

    # 模拟工具调用
    tool_calls = [
        {
            "id": "call_1",
            "function": {
                "name": "calculator",
                "arguments": '{"expression": "10 + 20"}',
            },
        },
        {
            "id": "call_2",
            "function": {"name": "weather", "arguments": '{"city": "上海"}'},
        },
    ]

    # 执行工具调用
    results = executor.execute_tool_calls(tool_calls)

    for result in results:
        print(f"工具调用 {result['tool_call_id']}: {result['result']}")


def demo_tool_node():
    """演示工具节点"""
    print("\n=== 工具节点演示 ===")

    # 创建工作流
    workflow = Workflow("工具工作流", {"prompt": "执行一些工具调用"})

    # 创建工具注册表
    registry = create_tool_registry()
    registry.register_tool(calculate)
    registry.register_tool(get_weather)

    # 创建工具节点
    tool_node = ToolNode("tool_executor", registry)

    # 添加节点到工作流
    workflow.nodes.append(tool_node)
    workflow.set_start_node("tool_executor")

    # 执行工作流
    result = workflow.run()
    print(f"工作流结果: {result.final_state}")


async def demo_advanced_features():
    """演示高级功能"""
    print("\n=== 高级功能演示 ===")

    registry = create_tool_registry()

    # 注册多个工具
    registry.register_tool(calculate)
    registry.register_tool(get_weather)
    registry.register_tool(async_process_data)

    # 创建执行器
    executor = ToolExecutor(registry)

    # 混合同步和异步工具调用
    tool_calls = [
        {
            "id": "sync_1",
            "function": {"name": "calculator", "arguments": '{"expression": "5 * 6"}'},
        },
        {
            "id": "async_1",
            "function": {
                "name": "async_processor",
                "arguments": '{"data": "test data"}',
            },
        },
    ]

    # 异步执行所有工具调用
    results = await executor.aexecute_tool_calls(tool_calls)

    for result in results:
        status = "成功" if result["status"] == "success" else "失败"
        print(f"工具 {result['name']} ({status}): {result['result']}")


def main():
    """主函数"""
    print("Lite Workflow 工具系统演示")
    print("=" * 50)

    # 基础功能演示
    demo_basic_tools()

    # 异步功能演示
    asyncio.run(demo_async_tools())

    # 工具执行器演示
    demo_tool_executor()

    # 工具节点演示
    demo_tool_node()

    # 高级功能演示
    asyncio.run(demo_advanced_features())

    print("\n演示完成！")


if __name__ == "__main__":
    main()
