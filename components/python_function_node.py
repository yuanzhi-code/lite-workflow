from definitions.node_types import BaseNode
from typing import Any, Dict, Callable

class PythonFunctionNode(BaseNode):
    """
    自定义Python函数或类节点。
    """
    def __init__(self, node_id: str, func: Callable, config: Dict = None):
        super().__init__(node_id, config)
        self.func = func

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"PythonFunctionNode {self.node_id} executing function: {self.func.__name__} with inputs: {inputs}")
        # 实际的Python函数调用逻辑
        try:
            result = self.func(inputs)
            return result # 直接返回函数结果，而不是嵌套在 'function_output' 中
        except Exception as e:
            print(f"Error in PythonFunctionNode {self.node_id}: {e}")
            return {"error": str(e)} 