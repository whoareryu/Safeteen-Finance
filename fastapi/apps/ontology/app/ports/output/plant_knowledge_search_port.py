from abc import ABC, abstractmethod


class PlantKnowledgeSearchPort(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 3) -> list[dict]: ...
