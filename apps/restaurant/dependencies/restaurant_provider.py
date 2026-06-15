from functools import lru_cache

from restaurant.app.ports.input.restaurant_use_case import RestaurantUseCase
from restaurant.app.ports.output.restaurant_repository import IRestaurantRepository
from restaurant.app.use_cases.restaurant_domain_interactor import RestaurantDomainInteractor
from user.app.use_cases.strategies.recommendation_strategy import (
    CategoryBrowseRecommendationStrategy,
)
from restaurant.adapter.outbound.pg.restaurant_pg_repository import RestaurantRepository


@lru_cache
def get_restaurant_use_case() -> RestaurantUseCase:
    repository: IRestaurantRepository = RestaurantRepository()
    return RestaurantDomainInteractor(
        repository=repository,
        browse_strategy=CategoryBrowseRecommendationStrategy(restaurant_repo=repository),
    )
