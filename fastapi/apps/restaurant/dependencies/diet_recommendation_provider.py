from functools import lru_cache

from restaurant.adapter.outbound.pg.diet_recommendation_pg_repository import (
    DietRecommendationPgRepository,
)
from restaurant.app.ports.input.diet_recommendation_use_case import (
    DietRecommendationUseCase,
)
from restaurant.app.use_cases.diet_recommendation_interactor import (
    DietRecommendationInteractor,
)


@lru_cache
def get_diet_recommendation_use_case() -> DietRecommendationUseCase:
    return DietRecommendationInteractor(repository=DietRecommendationPgRepository())
