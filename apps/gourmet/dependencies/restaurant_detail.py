from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_detail_pg_repository import RestaurantDetailPgRepository
from gourmet.app.ports.input.restaurant_detail_use_case import RestaurantDetailUseCase
from gourmet.app.ports.output.restaurant_detail_repository import RestaurantDetailRepository
from gourmet.app.use_cases.restaurant_detail_interactor import RestaurantDetailInteractor


@lru_cache
def get_restaurant_detail_use_case() -> RestaurantDetailUseCase:
    repository: RestaurantDetailRepository = RestaurantDetailPgRepository()
    return RestaurantDetailInteractor(repository=repository)
