from abc import ABC, abstractmethod


class TaskDispatchPort(ABC):
    @abstractmethod
    async def dispatch(self, task_type: str, payload: dict) -> dict: ...
