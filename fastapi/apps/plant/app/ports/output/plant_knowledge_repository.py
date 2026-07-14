from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.plant_knowledge_entity import PlantKnowledgeEntity


class PlantKnowledgeRepository(ABC):
    """RAG 지식베이스(plant_knowledge) 출력 포트 — 임베딩 코사인 유사도 검색."""

    @abstractmethod
    async def find_similar(self, embedding: list[float], limit: int) -> list[PlantKnowledgeEntity]:
        pass
