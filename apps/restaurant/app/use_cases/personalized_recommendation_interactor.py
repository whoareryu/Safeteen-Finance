from __future__ import annotations

from sqlalchemy.orm import Session

from restaurant.app.dtos.personalized_recommendation_dto import (
    PersonalizedPick,
    PersonalizedQuery,
)
from restaurant.app.ports.input.personalized_recommendation_use_case import (
    PersonalizedRecommendationUseCase,
)
from restaurant.app.ports.output.personalized_recommendation_repository import (
    PersonalizedRecommendationRepository,
)
from restaurant.app.use_cases.strategies.recommendation_scoring_strategy import (
    RecommendationScoringStrategy,
)

_SLOT_LABEL = {"morning": "아침", "lunch": "점심", "dinner": "저녁"}
_CANDIDATE_POOL = 200


class PersonalizedRecommendationInteractor(PersonalizedRecommendationUseCase):
    def __init__(
        self,
        repository: PersonalizedRecommendationRepository,
        strategy: RecommendationScoringStrategy,
    ) -> None:
        self._repository = repository
        self._strategy = strategy

    def pick_one(self, db: Session, query: PersonalizedQuery) -> PersonalizedPick:
        candidates = self._repository.candidate_restaurants(
            db,
            excluded_ids=query.preference.excluded_restaurant_ids,
            limit=_CANDIDATE_POOL,
        )
        if not candidates:
            raise ValueError("추천할 식당이 없습니다.")

        best = max(candidates, key=lambda c: self._strategy.score(c, query))
        return PersonalizedPick(
            id=best["id"],
            name=best["name"],
            genre=best.get("genre", ""),
            road_address=best.get("road_address", ""),
            latitude=best.get("latitude"),
            longitude=best.get("longitude"),
            reason=self._reason(best, query),
        )

    def _reason(self, candidate: dict, query: PersonalizedQuery) -> str:
        genre = candidate.get("genre", "")
        ranking = query.preference.genre_ranking
        if genre in ranking or candidate.get("slug", "") in ranking:
            return f"취향에 맞는 {genre} 한 곳이에요."
        slot = _SLOT_LABEL.get(query.time_slot, "오늘")
        return f"{slot}에 어울리는 {genre} 추천이에요."
