from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class DietRecommendationRepository(ABC):
    """식단 조건에 해당하는 카테고리 slug 기반 식당 조회 포트."""

    @abstractmethod
    def find_by_slugs(
        self, db: Session, *, slugs: list[str], district: str | None, limit: int
    ) -> list[dict]:
        ...
