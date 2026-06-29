from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class PersonalizedRecommendationRepository(ABC):
    """후보 식당 조회 포트 (제외 식당 필터 포함)."""

    @abstractmethod
    def candidate_restaurants(
        self, db: Session, *, excluded_ids: list[int], limit: int
    ) -> list[dict]:
        ...
