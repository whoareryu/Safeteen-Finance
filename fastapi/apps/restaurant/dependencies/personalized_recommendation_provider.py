from functools import lru_cache

from restaurant.adapter.outbound.pg.personalized_recommendation_pg_repository import (
    PersonalizedRecommendationPgRepository,
)
from restaurant.app.ports.input.personalized_recommendation_use_case import (
    PersonalizedRecommendationUseCase,
)
from restaurant.app.use_cases.personalized_recommendation_interactor import (
    PersonalizedRecommendationInteractor,
)
from restaurant.app.use_cases.strategies.context_scoring_strategy import (
    ContextScoringStrategy,
)


@lru_cache
def get_personalized_recommendation_use_case() -> PersonalizedRecommendationUseCase:
    return PersonalizedRecommendationInteractor(
        repository=PersonalizedRecommendationPgRepository(),
        strategy=ContextScoringStrategy(),
    )
