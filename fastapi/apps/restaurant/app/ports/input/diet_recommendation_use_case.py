from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from restaurant.app.dtos.diet_recommendation_dto import DietQuery, DietView


class DietRecommendationUseCase(ABC):
    """고단백/저탄수 등 식단 조건 식당 추천 (기획서 3-4)."""

    @abstractmethod
    def recommend(self, db: Session, query: DietQuery) -> DietView:
        ...
