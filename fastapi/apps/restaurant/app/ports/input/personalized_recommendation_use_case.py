from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from restaurant.app.dtos.personalized_recommendation_dto import (
    PersonalizedPick,
    PersonalizedQuery,
)


class PersonalizedRecommendationUseCase(ABC):
    """광고 비개입 개인화 추천 엔진 (기획서 4-1). 메인 홈 '1곳' 추천."""

    @abstractmethod
    def pick_one(self, db: Session, query: PersonalizedQuery) -> PersonalizedPick:
        ...
