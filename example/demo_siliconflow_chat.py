import asyncio
import os
import sys
import time

# 确保能导入 lite_workflow 模块
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from lite_workflow.components.chat_models import ChatSiliconFlow, Message
from lite_workflow.core.error_handler import ErrorHandler, ErrorPolicy
from lite_workflow.core.state_manager import StateManager
from lite_workflow.definitions.edge import Edge
from lite_workflow.definitions.graph import Graph
from lite_workflow.definitions.node import create_function_node
from lite_workflow.engine.pregel_engine import PregelEngine

# 节点实现


def initial_prompt_node(inputs: dict) -> dict:
    """处理初始输入并准备好进行大模型调用。"""
    prompt = inputs.get("prompt", "请用中文简洁介绍一下机器学习。")
    print(f"📝 [开始] 接收到提示: {prompt}")
    return {"prompt": prompt}


async def silicon_flow_chat_node(inputs: dict) -> dict:
    """调用硅基流动模型生成回复。"""
    user_prompt = inputs.get("prompt", "")
    print(f"💬 [硅基流动] 输入: {user_prompt}")
    if not user_prompt:
        return {"error": "未提供用户提示", "model_response": ""}

    # 检查 API KEY
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print("❌ [硅基流动] 未设置 SILICONFLOW_API_KEY 环境变量")
        return {"error": "未设置 SILICONFLOW_API_KEY 环境变量", "model_response": ""}

    print(f"🔑 [硅基流动] API KEY 已设置: {api_key[:10]}...")

    try:
        print("🚀 [硅基流动] 正在创建模型实例...")
        model = ChatSiliconFlow(model="Qwen/Qwen3-8B", api_key=api_key)
        print("✅ [硅基流动] 模型实例创建成功")

        print("📤 [硅基流动] 正在调用模型...")
        messages = [Message.user(user_prompt)]
        result = await model.ainvoke(messages)
        model_response = result.content
        print(f"✨ [硅基流动] 模型回复: {model_response[:100]}...")
        return {"model_response": model_response, "original_prompt": user_prompt}
    except Exception as e:
        print(f"❌ [硅基流动] 模型调用失败: {e}")
        print(f"❌ [硅基流动] 错误类型: {type(e).__name__}")
        import traceback

        print(f"❌ [硅基流动] 错误堆栈: {traceback.format_exc()}")
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


# 图结构构建器


def create_siliconflow_graph() -> Graph:
    """创建包含硅基流动调用的图结构。"""
    nodes = [
        create_function_node("initial_prompt", initial_prompt_node),
        create_function_node("silicon_flow_chat", silicon_flow_chat_node),
        create_function_node("final_output", final_output_node),
    ]
    edges = [
        Edge("initial_prompt", "silicon_flow_chat"),
        Edge("silicon_flow_chat", "final_output"),
    ]
    return Graph("siliconflow_chat_demo", nodes, edges, "initial_prompt")


# 执行函数


async def run_siliconflow_demo():
    """运行硅基流动图编排测试。"""
    print("🎯 硅基流动聊天图编排测试")
    print("=" * 60)

    graph = create_siliconflow_graph()
    print(f"📊 图已构建: {len(graph.nodes)} 节点, {len(graph.edges)} 边")
    print(f"   起始节点: {graph.start_node}")
    print(f"   终止节点: {[n for n in graph.nodes if graph.is_terminal(n)]}")

    print(f"✅ 图验证: {graph.validate_cycles()}")

    initial_state = {"prompt": "请用一句话介绍什么是人工智能。"}
    state_manager = StateManager(initial_state)
    error_handler = ErrorHandler()

    # 设置错误处理策略为快速失败，这样可以看到具体错误
    error_handler.default_policy = ErrorPolicy.FAIL_FAST
    engine = PregelEngine(graph, state_manager, error_handler)

    print("\n🔄 开始执行...")
    print(f"初始状态: {initial_state}")

    start_time = time.time()
    final_state = await engine.execute_async()
    execution_time = time.time() - start_time

    print("\n🎉 执行完成!")
    print(f"总耗时: {execution_time:.2f}s")

    final_data = final_state.to_dict()
    print("\n📋 最终结果:")
    print(final_data.get("final_output", {}))

    print("\n📈 执行统计:")
    stats = engine.get_execution_stats()

    # 格式化时间显示
    def format_duration(seconds):
        if seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}分{remaining_seconds:.1f}秒"

    def format_timestamp(timestamp):
        from datetime import datetime

        return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    # 显示友好的统计信息
    print(f"   ⏱️  总耗时: {format_duration(stats.get('total_duration', 0))}")
    print(f"   🕐  开始时间: {format_timestamp(stats.get('start_time', 0))}")
    print(f"   🕐  结束时间: {format_timestamp(stats.get('end_time', 0))}")
    print(f"   🔄  超步数量: {stats.get('total_supersteps', 0)}")
    print(f"   ⚙️  执行节点: {stats.get('total_nodes_executed', 0)}")
    print(f"   📨  消息传递: {stats.get('messages_sent', 0)}")

    # 显示节点执行时间详情
    node_times = stats.get("node_execution_times", {})
    if node_times:
        print("   ⏱️  节点耗时详情:")
        for node_id, duration in node_times.items():
            print(f"      • {node_id}: {format_duration(duration)}")

    return {
        "success": True,
        "final_state": final_data,
        "execution_stats": stats,
        "execution_time": execution_time,
    }


if __name__ == "__main__":
    asyncio.run(run_siliconflow_demo())
