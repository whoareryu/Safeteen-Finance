from abc import ABC, abstractmethod

from plant.app.dtos.knowledge_sync_dto import KnowledgeSyncResult


class KnowledgeSyncUseCase(ABC):
    @abstractmethod
    async def sync(self) -> KnowledgeSyncResult: ...
