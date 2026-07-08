from functools import lru_cache

from restaurant.adapter.outbound.pg.restaurant_detail_pg_repository import RestaurantDetailPgRepository
from restaurant.app.ports.input.restaurant_detail_use_case import RestaurantDetailUseCase
from restaurant.app.ports.output.restaurant_detail_repository import RestaurantDetailRepository
from restaurant.app.use_cases.restaurant_detail_interactor import RestaurantDetailInteractor


@lru_cache
def get_restaurant_detail_use_case() -> RestaurantDetailUseCase:
    repository: RestaurantDetailRepository = RestaurantDetailPgRepository()
    return RestaurantDetailInteractor(repository=repository)
