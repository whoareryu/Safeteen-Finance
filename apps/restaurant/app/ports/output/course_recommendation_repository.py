from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class CourseRecommendationRepository(ABC):
    """코스 구성용 식당 조회 포트."""

    @abstractmethod
    def find_one_by_district_and_slot(
        self, db: Session, *, district: str, category_slug: str
    ) -> dict | None:
        ...
