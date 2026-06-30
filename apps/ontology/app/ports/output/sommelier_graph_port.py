from abc import ABC, abstractmethod


class SommelierPort(ABC):
    @abstractmethod
    async def run_cypher(self, cypher: str, params: dict) -> list[dict]: ...
