from abc import ABC, abstractmethod


class LensPort(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    async def search_by_vector(
        self, collection: str, vector: list[float], limit: int
    ) -> list[dict]: ...
