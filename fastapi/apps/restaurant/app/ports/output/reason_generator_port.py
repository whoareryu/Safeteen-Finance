from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.personalized_recommendation_dto import PersonalizedQuery


class ReasonGeneratorPort(ABC):
    """추천 후보에 대한 자연어 이유 문구 생성 포트 (OCP — 템플릿/LLM 등 교체 가능)."""

    @abstractmethod
    async def generate(self, candidate: dict, query: PersonalizedQuery) -> str:
        ...
