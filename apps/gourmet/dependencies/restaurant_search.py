from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_search_pg_repository import RestaurantSearchPgRepository
from gourmet.app.ports.input.restaurant_search_use_case import RestaurantSearchUseCase
from gourmet.app.ports.output.restaurant_search_repository import RestaurantSearchRepository
from gourmet.app.use_cases.restaurant_search_interactor import RestaurantSearchInteractor


@lru_cache
def get_restaurant_search_use_case() -> RestaurantSearchUseCase:
    repository: RestaurantSearchRepository = RestaurantSearchPgRepository()
    return RestaurantSearchInteractor(repository=repository)
