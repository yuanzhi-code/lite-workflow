import asyncio
import os
import sys
import time

# 确保能导入lite_workflow模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from lite_workflow.components.chat_models import ChatSiliconFlow, Message
from lite_workflow.core.error_handler import ErrorHandler
from lite_workflow.core.state_manager import StateManager
from lite_workflow.definitions.edge import Edge
from lite_workflow.definitions.graph import Graph
from lite_workflow.definitions.node import (
    create_async_function_node,
    create_function_node,
)
from lite_workflow.engine.pregel_engine import PregelEngine

# 初始化硅基流动模型
# 请确保已设置 OPENAI_API_KEY 或 SILICONFLOW_API_KEY 环境变量
# 例如: export SILICONFLOW_API_KEY='YOUR_API_KEY'
try:
    silicon_flow_model = ChatSiliconFlow(model="Qwen/Qwen3-8B")  # 您也可以尝试其他模型
    print("✅ 硅基流动模型初始化成功！")
except ValueError as e:
    print(f"❌ 硅基流动模型初始化失败: {e}")
    print("请确保已设置 OPENAI_API_KEY 或 SILICONFLOW_API_KEY 环境变量。")
    exit(1)


# 🎯 节点实现


def initial_prompt_node(inputs: dict) -> dict:
    """处理初始输入并准备好进行大模型调用。"""
    prompt = inputs.get("prompt", "请用中文简洁介绍一下机器学习。")
    print(f"📝 [开始] 接收到提示: {prompt}")
    return {"prompt": prompt}


async def silicon_flow_chat_node(inputs: dict) -> dict:
    """调用硅基流动模型生成回复。"""
    user_prompt = inputs.get("prompt", "")  # 将 "user_prompt" 改为 "prompt"
    print(f"💬 [硅基流动] 接收到的输入 (inputs): {inputs}")  # 添加这行来调试
    if not user_prompt:
        return {"error": "未提供用户提示", "model_response": ""}

    print("💬 [硅基流动] 正在调用模型生成回复...")
    try:
        # 将字符串提示转换为Message对象列表
        messages = [Message.user(user_prompt)]
        result = await silicon_flow_model.ainvoke(messages)
        model_response = result.message.content
        print(f"✨ [硅基流动] 模型回复: {model_response[:100]}...")  # 打印部分回复
        return {"model_response": model_response, "original_prompt": user_prompt}
    except Exception as e:
        print(f"❌ [硅基流动] 模型调用失败: {e}")
        return {"error": str(e), "model_response": ""}


def final_output_node(inputs: dict) -> dict:
    """整理并输出最终结果。"""
    original_prompt = inputs.get("original_prompt", "无")
    model_response = inputs.get("model_response", "无回复")
    error = inputs.get("error", None)

    print("🎉 [完成] 最终结果：")
    print(f"   原始提示: {original_prompt}")
    if error:
        print(f"   错误信息: {error}")
    print(f"   模型回复: {model_response}")

    return {
        "final_output": {
            "original_prompt": original_prompt,
            "model_response": model_response,
            "error": error,
        }
    }


# 🏗️ 图结构构建器


def create_siliconflow_graph() -> Graph:
    """创建包含硅基流动调用的图结构。"""
    nodes = [
        create_function_node("initial_prompt", initial_prompt_node),
        create_async_function_node(
            "silicon_flow_chat", silicon_flow_chat_node
        ),  # 标记为异步节点
        create_function_node("final_output", final_output_node),
    ]

    edges = [
        Edge("initial_prompt", "silicon_flow_chat"),
        Edge("silicon_flow_chat", "final_output"),
    ]

    return Graph("siliconflow_chat_demo", nodes, edges, "initial_prompt")


# 🚀 执行函数


async def run_siliconflow_demo():
    """运行硅基流动图演示。"""
    print("🎯 硅基流动聊天图演示")
    print("=" * 60)

    graph = create_siliconflow_graph()
    print(f"📊 图已构建: {len(graph.nodes)} 节点, {len(graph.edges)} 边")
    print(f"   起始节点: {graph.start_node}")
    print(f"   终止节点: {[n for n in graph.nodes if graph.is_terminal(n)]}")

    print(f"✅ 图验证: {graph.validate_cycles()}")

    initial_state = {"prompt": "请解释一下大语言模型的工作原理，用100字以内概括。"}
    state_manager = StateManager(initial_state)
    error_handler = ErrorHandler()

    engine = PregelEngine(graph, state_manager, error_handler)

    print("\n🔄 开始执行...")
    print(f"初始状态: {initial_state}")

    start_time = time.time()
    final_state = await engine.execute_async()  # 使用异步执行
    execution_time = time.time() - start_time

    print("\n🎉 执行完成!")
    print(f"总耗时: {execution_time:.2f}s")

    final_data = final_state.to_dict()
    print("\n�� 最终结果:")
    print(f"完整最终数据: {final_data}")  # 添加此行
    print(final_data.get("final_output", {}))

    print("\n📈 执行统计:")
    stats = engine.get_execution_stats()
    for key, value in stats.items():
        if key != "node_execution_times":
            print(f"   {key}: {value}")

    return {
        "success": True,
        "final_state": final_data,
        "execution_stats": stats,
        "execution_time": execution_time,
    }


if __name__ == "__main__":
    asyncio.run(run_siliconflow_demo())
