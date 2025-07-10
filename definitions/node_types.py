from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseNode(ABC):
    """
    所有节点的抽象基类。
    定义了节点必须实现的核心接口。
    """
    def __init__(self, node_id: str, config: Dict = None):
        self.node_id = node_id
        self.config = config if config is not None else {}

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行节点的具体操作。
        参数：
            inputs (Dict[str, Any]): 来自上游节点或当前状态的输入数据。
        返回：
            Dict[str, Any]: 节点执行后的输出数据，用于更新整体状态或传递给下游节点。
        """
        pass 