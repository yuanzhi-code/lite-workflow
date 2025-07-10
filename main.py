from definitions.graph import Node, Edge, Graph
from definitions.state import State
from components.llm_node import LLMNode
from components.tool_node import ToolNode
from components.python_function_node import PythonFunctionNode
from core.state_manager import StateManager
from core.error_handler import ErrorHandler
from engine.execution_engine import ExecutionEngine
from typing import Dict, Any

# --- 辅助 Python 函数定义 ---
def initial_data_processor(input_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Function] Initial Data Processor received: {input_data}")
    # 从input_data中获取prompt
    prompt = input_data.get("prompt", "")
    # 确保返回的字典键不与现有全局状态键冲突，如果需要覆盖则明确
    return {"processed_initial_data": prompt.upper(), "counter": 0}

def fan_out_logic(input_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Function] Fan-Out Logic received: {input_data}")
    # 从input_data中获取processed_initial_data，它可能来自上一个PythonFunctionNode的输出
    processed_initial_data = input_data.get("processed_initial_data", "")
    if not processed_initial_data: # 如果没有找到，尝试从其他可能的键中获取，例如原始prompt
        processed_initial_data = input_data.get("prompt", "")
        print(f"[Fan-Out Logic] Using prompt as processed_initial_data: {processed_initial_data}")

    # 模拟数据分发
    return {"path_A_input": processed_initial_data, "path_B_input": processed_initial_data + "_TOOL_QUERY"}

def fan_in_aggregator(input_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Function] Fan-In Aggregator received: {input_data}")
    # 假设输入包含来自不同路径的数据
    # LLMNode和ToolNode直接返回了llm_output和tool_output
    llm_output = input_data.get("llm_output", 'N/A')
    tool_output = input_data.get("tool_output", 'N/A')
    aggregated_result = f"Aggregated: LLM Output=[{llm_output}], Tool Output=[{tool_output}]"
    
    # 传递 counter 以便循环使用，counter 应该在顶层，因为它是被状态管理器更新的
    counter = input_data.get("counter", 0)
    return {"aggregated_data": aggregated_result, "counter": counter}

def loop_body_increment(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # 从input_data中获取counter
    current_counter = input_data.get("counter", 0)
    new_counter = current_counter + 1
    print(f"[Function] Loop Body: Counter incremented to {new_counter}")
    # 返回新的counter值，确保它是顶层键，以便状态管理器更新
    return {"counter": new_counter, "loop_data": f"Iteration {new_counter} data: {input_data.get('aggregated_data', 'N/A')}"}

def loop_condition_check(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # 从input_data中获取counter
    current_counter = input_data.get("counter", 0)
    should_continue = current_counter < 3 # 循环3次
    print(f"[Function] Loop Condition Check: Counter={current_counter}, Continue Loop={should_continue}")
    # 返回 should_continue_loop 和 final_message，确保是顶层键
    return {"should_continue_loop": should_continue, "final_message": f"Loop finished at counter {current_counter}"}

def final_processor(input_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Function] Final Processor received: {input_data}")
    # 从input_data中获取final_message
    final_message = input_data.get("final_message", 'N/A')
    return {"final_result": f"Workflow completed. Final message: {final_message}"}


if __name__ == "__main__":
    print("--- 开始构建工作流示例 (包含扇入、扇出、循环和条件边) ---")

    # 1. 定义节点
    node1 = Node("start_node", "PythonFunction", config={
        "function_ref": initial_data_processor
    })
    node2 = Node("fan_out_node", "PythonFunction", config={
        "function_ref": fan_out_logic
    })
    node3 = Node("path_A_llm", "LLM", config={
        "llm_model": "GPT-4"
    })
    node4 = Node("path_B_tool", "Tool", config={
        "tool_name": "web_search"
    })
    node5 = Node("fan_in_aggregator", "PythonFunction", config={
        "function_ref": fan_in_aggregator
    })
    node6 = Node("loop_body", "PythonFunction", config={
        "function_ref": loop_body_increment
    })
    node7 = Node("loop_condition", "PythonFunction", config={
        "function_ref": loop_condition_check
    })
    node8 = Node("final_node", "LLM", config={
        "llm_model": "Claude-3-Opus"
    })

    # 2. 定义边
    edges = [
        # 扇出
        Edge("start_node", "fan_out_node"),
        Edge("fan_out_node", "path_A_llm"),
        Edge("fan_out_node", "path_B_tool"),

        # 扇入
        Edge("path_A_llm", "fan_in_aggregator"),
        Edge("path_B_tool", "fan_in_aggregator"),
        
        # 循环 (通过条件边实现)
        Edge("fan_in_aggregator", "loop_body"),
        Edge("loop_body", "loop_condition"),
        # 条件边：如果 should_continue_loop 为 True，则返回 loop_body 形成循环
        Edge("loop_condition", "loop_body", condition="output.should_continue_loop == True"), 
        # 条件边：如果 should_continue_loop 为 False，则退出循环到 final_node
        Edge("loop_condition", "final_node", condition="output.should_continue_loop == False"),
    ]

    nodes = [node1, node2, node3, node4, node5, node6, node7, node8]

    # 3. 创建图
    workflow_graph = Graph("complex_workflow_demo", nodes, edges, "start_node")

    # 4. 初始化状态管理器和错误处理器
    initial_state = {"prompt": "Test workflow with fan-in, fan-out, loops, and conditional edges."}
    state_manager = StateManager(initial_state=initial_state)
    error_handler = ErrorHandler()

    # 注册一个简单的错误回调 (示例)
    def custom_error_callback(node_id: str, exception: Exception, inputs: Dict[str, Any]):
        print(f"[Error Callback] Node {node_id} encountered an error: {exception}. Inputs: {inputs}")
    error_handler.register_error_callback("path_B_tool", custom_error_callback)

    # 5. 初始化执行引擎
    engine = ExecutionEngine(workflow_graph, state_manager, error_handler)

    print("--- 开始执行复杂工作流 ---")
    final_state = engine.run()

    print("--- 工作流执行完成 ---")
    print("最终状态:")
    print(final_state.to_dict())

    print("\n--- 注意事项 ---")
    print("1. 条件边评估：`_evaluate_condition` 目前使用简单的字符串匹配，生产环境应替换为安全的表达式解析器。")
    print("2. 并行执行：目前节点在每个超步内是顺序执行的，并行执行尚未实现。")
    print("3. 循环终止：循环通过 `loop_condition` 节点判断 `counter` 来控制。")
