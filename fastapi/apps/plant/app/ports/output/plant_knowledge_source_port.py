from abc import ABC, abstractmethod

from plant.app.dtos.knowledge_sync_dto import PlantKnowledgeFact


class PlantKnowledgeSourcePort(ABC):
    @abstractmethod
    def fetch_all(self) -> list[PlantKnowledgeFact]: ...
