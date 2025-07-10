from typing import Dict, Any, Callable
from definitions.state import State, IncrementalUpdate

class StateManager:
    """
    负责管理和合并工作流的全局状态。
    借鉴Pregel的消息传递式状态更新思想。
    """
    def __init__(self, initial_state: Dict[str, Any] = None):
        self._global_state = State(initial_state)

    def get_global_state(self) -> State:
        return self._global_state

    def apply_incremental_update(self, update: IncrementalUpdate) -> None:
        """
        应用来自节点的增量状态更新。
        """
        for key, value in update.updates.items():
            if update.conflict_strategy == 'overwrite':
                self._global_state.set(key, value)
            elif update.conflict_strategy == 'ignore':
                if self._global_state.get(key) is None:
                    self._global_state.set(key, value)
            elif update.conflict_strategy == 'merge':
                # 这里可以实现更复杂的合并逻辑，例如合并字典或列表
                # 简单示例：如果都是字典，尝试合并，否则覆盖
                current_value = self._global_state.get(key)
                if isinstance(current_value, dict) and isinstance(value, dict):
                    merged_value = current_value.copy()
                    merged_value.update(value)
                    self._global_state.set(key, merged_value)
                else:
                    self._global_state.set(key, value)
            else:
                # 默认行为或抛出错误
                self._global_state.set(key, value)

    def register_custom_merge_strategy(self, key: str, strategy: Callable[[Any, Any], Any]):
        """
        注册自定义的合并策略（MVP后考虑）。
        """
        # TODO: Implement custom merge strategies if needed
        pass 