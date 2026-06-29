from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.personalized_recommendation_dto import PersonalizedQuery


class RecommendationScoringStrategy(ABC):
    """추천 점수 알고리즘 교체 지점 (OCP).

    시간대·날씨·취향 가중치를 바꾸려면 Interactor를 고치지 말고 새 전략을 추가한다.
    """

    @abstractmethod
    def score(self, candidate: dict, query: PersonalizedQuery) -> float:
        ...
