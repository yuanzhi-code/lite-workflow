from typing import Dict, Any, Literal

class State:
    """
    表示工作流的当前全局状态。
    """
    def __init__(self, initial_data: Dict[str, Any] = None):
        self._data = initial_data if initial_data is not None else {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def update(self, new_data: Dict[str, Any]):
        self._data.update(new_data)

    def to_dict(self) -> Dict[str, Any]:
        return self._data

class IncrementalUpdate:
    """
    表示对全局状态的增量更新。
    """
    def __init__(self, updates: Dict[str, Any], conflict_strategy: Literal['overwrite', 'ignore', 'merge'] = 'overwrite'):
        self.updates = updates
        self.conflict_strategy = conflict_strategy 