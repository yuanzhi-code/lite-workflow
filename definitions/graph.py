from typing import List, Dict, Any, Optional

class Node:
    """
    表示图中的一个节点。
    """
    def __init__(self, node_id: str, node_type: str, config: Dict = None):
        self.node_id = node_id
        self.node_type = node_type # LLM, Tool, PythonFunction, etc.
        self.config = config if config is not None else {}
        self.inputs: Dict[str, Any] = {} # 运行时输入，由边传输
        self.outputs: Dict[str, Any] = {} # 运行时输出

class Edge:
    """
    表示图中节点之间的数据流和控制流。
    """
    def __init__(self, source_node_id: str, target_node_id: str, condition: Optional[str] = None):
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.condition = condition # 条件边（可选）

class Graph:
    """
    表示整个工作流的图结构。
    """
    def __init__(self, graph_id: str, nodes: List[Node], edges: List[Edge], start_node_id: str):
        self.graph_id = graph_id
        self.nodes_map: Dict[str, Node] = {node.node_id: node for node in nodes}
        self.edges: List[Edge] = edges
        self.start_node_id = start_node_id

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes_map.get(node_id)

    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        return [edge for edge in self.edges if edge.source_node_id == node_id]

    def get_incoming_edges(self, node_id: str) -> List[Edge]:
        return [edge for edge in self.edges if edge.target_node_id == node_id] 