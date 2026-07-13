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
from restaurant.app.ports.output.reason_generator_port import ReasonGeneratorPort
from restaurant.app.use_cases.strategies.recommendation_scoring_strategy import (
    RecommendationScoringStrategy,
)

_CANDIDATE_POOL = 200


class PersonalizedRecommendationInteractor(PersonalizedRecommendationUseCase):
    def __init__(
        self,
        repository: PersonalizedRecommendationRepository,
        strategy: RecommendationScoringStrategy,
        reason_generator: ReasonGeneratorPort,
    ) -> None:
        self._repository = repository
        self._strategy = strategy
        self._reason_generator = reason_generator

    async def pick_one(self, db: Session, query: PersonalizedQuery) -> PersonalizedPick:
        candidates = self._repository.candidate_restaurants(
            db,
            excluded_ids=query.preference.excluded_restaurant_ids,
            limit=_CANDIDATE_POOL,
            lat=query.lat,
            lng=query.lng,
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
            reason=await self._reason_generator.generate(best, query),
        )
