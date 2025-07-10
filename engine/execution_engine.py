from typing import Dict, Any, List, Callable
from definitions.graph import Graph, Node, Edge
from definitions.state import State, IncrementalUpdate
from definitions.node_types import BaseNode
from core.state_manager import StateManager
from core.error_handler import ErrorHandler

# 导入具体节点类型，以便在引擎中实例化它们
from components.llm_node import LLMNode
from components.tool_node import ToolNode
from components.python_function_node import PythonFunctionNode

class ExecutionEngine:
    """
    工作流的执行引擎，负责图的遍历、节点执行和状态管理。
    """
    def __init__(self, graph: Graph, state_manager: StateManager, error_handler: ErrorHandler):
        self.graph = graph
        self.state_manager = state_manager
        self.error_handler = error_handler
        self._node_instance_cache: Dict[str, BaseNode] = {}

    def _get_node_instance(self, node: Node) -> BaseNode:
        """
        获取或创建节点的具体实例。
        """
        if node.node_id not in self._node_instance_cache:
            if node.node_type == 'LLM':
                # 假设LLMNode需要一个'llm_model'配置
                instance = LLMNode(node.node_id, node.config.get('llm_model', 'default_llm'), node.config)
            elif node.node_type == 'Tool':
                # 假设ToolNode需要一个'tool_name'配置
                instance = ToolNode(node.node_id, node.config.get('tool_name', 'default_tool'), node.config)
            elif node.node_type == 'PythonFunction':
                # PythonFunctionNode需要一个可调用的函数对象
                func_ref = node.config.get('function_ref')
                if not callable(func_ref):
                    raise ValueError(f"Node {node.node_id} of type PythonFunction requires a callable 'function_ref' in config.")
                instance = PythonFunctionNode(node.node_id, func_ref, node.config)
            else:
                raise ValueError(f"Unsupported node type: {node.node_type}")
            self._node_instance_cache[node.node_id] = instance
        return self._node_instance_cache[node.node_id]

    def _evaluate_condition(self, condition: str, node_outputs: Dict[str, Any], global_state: State) -> bool:
        """
        评估条件边的表达式。
        目前支持简单的 'key == value' 或 'output.key == value' 或 'state.key == value' 格式。
        注意：使用 eval 存在安全风险，生产环境应替换为安全的表达式解析器。
        """
        if not condition:
            return True # 没有条件则默认为真

        # 尝试解析简单的条件表达式: key == value
        try:
            if "==" in condition:
                parts = condition.split("==", 1)
                key = parts[0].strip()
                expected_value_str = parts[1].strip().strip("'\"") # 移除引号
                
                actual_value = None
                if key.startswith("output."):
                    output_key = key.split("output.")[1]
                    actual_value = node_outputs.get(output_key)
                elif key.startswith("state."):
                    state_key = key.split("state.")[1]
                    actual_value = global_state.get(state_key)
                else: # 默认为检查节点输出
                    actual_value = node_outputs.get(key)

                return str(actual_value) == expected_value_str
            
            # 如果条件只是一个key，检查其在node_outputs中是否为真
            return bool(node_outputs.get(condition))

        except Exception as e:
            print(f"Warning: Error evaluating condition '{condition}': {e}")
            return False # 评估失败则条件不满足

    def run(self) -> State:
        """
        执行整个工作流，采用Pregel风格的超步（Superstep）执行模型。
        """
        self.state_manager.get_global_state().set("superstep", 0) # 追踪超步
        
        # 初始化节点接收消息的队列
        node_incoming_messages: Dict[str, List[Dict[str, Any]]] = {node_id: [] for node_id in self.graph.nodes_map.keys()}
        
        # 初始消息发送给起始节点，包含初始全局状态
        start_node_id = self.graph.start_node_id
        if not start_node_id:
            raise ValueError("Graph must have a start node defined.")
        
        node_incoming_messages[start_node_id].append(self.state_manager.get_global_state().to_dict())

        while True:
            current_superstep = self.state_manager.get_global_state().get("superstep")
            
            # 1. 节点激活阶段：识别本超步中需要执行的节点
            active_nodes_in_superstep: List[Node] = []
            for node_id, messages in node_incoming_messages.items():
                if messages: # 节点收到消息，则激活
                    node = self.graph.get_node(node_id)
                    if node:
                        active_nodes_in_superstep.append(node)
            
            print(f"\n--- 超步 {current_superstep} 开始 --- (活跃节点: {[node.node_id for node in active_nodes_in_superstep]})")

            # 存储本超步执行后，发给下一超步节点的消息
            next_superstep_messages: Dict[str, List[Dict[str, Any]]] = {node_id: [] for node_id in self.graph.nodes_map.keys()}
            
            if not active_nodes_in_superstep: # 没有活跃节点，且没有消息传递，工作流终止
                print("所有节点均不活跃且无新消息，工作流结束。")
                break

            # 2. 节点执行阶段
            # TODO: 在这里实现并行执行，当前是顺序执行
            for node in active_nodes_in_superstep:
                print(f"  -> 执行节点: {node.node_id} (类型: {node.node_type})")

                try:
                    node_instance = self._get_node_instance(node)
                    
                    # 聚合当前节点收到的所有消息作为其输入 (扇入)
                    aggregated_inputs: Dict[str, Any] = {}
                    for msg in node_incoming_messages[node.node_id]:
                        # 简单的合并策略：后收到的消息覆盖先收到的同名键
                        aggregated_inputs.update(msg)
                    
                    # 将当前全局状态也作为输入的一部分，方便节点查询
                    full_inputs = {**self.state_manager.get_global_state().to_dict(), **aggregated_inputs}

                    node_outputs = node_instance.execute(full_inputs)

                    # 将节点输出作为增量更新应用到全局状态 (消息传递到全局状态)
                    update = IncrementalUpdate(node_outputs, conflict_strategy='overwrite')
                    self.state_manager.apply_incremental_update(update)
                    print(f"    输出并更新状态: {node_outputs}")

                    # 3. 消息发送阶段：根据出边和条件，将输出发送给下游节点 (扇出)
                    outgoing_edges = self.graph.get_outgoing_edges(node.node_id)
                    for edge in outgoing_edges:
                        if self._evaluate_condition(edge.condition, node_outputs, self.state_manager.get_global_state()):
                            next_superstep_messages[edge.target_node_id].append(node_outputs) # 将本节点输出作为消息发送
                            print(f"      消息从 {node.node_id} 发送至 {edge.target_node_id} (条件满足)")
                        else:
                            print(f"      消息从 {node.node_id} 至 {edge.target_node_id} 未发送 (条件不满足: {edge.condition})")

                except Exception as e:
                    print(f"    节点 {node.node_id} 执行出错: {e}")
                    if not self.error_handler.handle_error(node.node_id, e, full_inputs):
                        print(f"    错误未处理，工作流停止。")
                        return self.state_manager.get_global_state()
            
            # 准备下一超步：将本超步生成的消息作为下一超步的输入消息
            node_incoming_messages = next_superstep_messages
            
            # 检查终止条件：如果本超步没有活跃节点，且没有为下一超步生成任何消息，则终止
            if not active_nodes_in_superstep and all(not msgs for msgs in node_incoming_messages.values()):
                print("--- 工作流终止: 无活跃节点且无新消息。---")
                break

            self.state_manager.get_global_state().set("superstep", current_superstep + 1)
            
        print("--- 工作流执行完毕。 ---")
        return self.state_manager.get_global_state()