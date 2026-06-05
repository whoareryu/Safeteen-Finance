from functools import lru_cache

from gourmet.app.ports.input.restaurant_use_case import RestaurantUseCase
from gourmet.app.ports.output.restaurant_repository import IRestaurantRepository
from gourmet.app.use_cases.restaurant_domain_interactor import RestaurantDomainInteractor
from gourmet.app.use_cases.strategies.recommendation_strategy import (
    CategoryBrowseRecommendationStrategy,
)
from gourmet.adapter.outbound.pg.restaurant_repository import RestaurantRepository


@lru_cache
def get_restaurant_use_case() -> RestaurantUseCase:
    repository: IRestaurantRepository = RestaurantRepository()
    return RestaurantDomainInteractor(
        repository=repository,
        browse_strategy=CategoryBrowseRecommendationStrategy(restaurant_repo=repository),
    )
