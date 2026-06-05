from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_browse_pg_repository import RestaurantBrowsePgRepository
from gourmet.app.ports.input.restaurant_browse_use_case import RestaurantBrowseUseCase
from gourmet.app.ports.output.restaurant_browse_repository import RestaurantBrowseRepository
from gourmet.app.use_cases.restaurant_browse_interactor import RestaurantBrowseInteractor


@lru_cache
def get_restaurant_browse_use_case() -> RestaurantBrowseUseCase:
    repository: RestaurantBrowseRepository = RestaurantBrowsePgRepository()
    return RestaurantBrowseInteractor(repository=repository)
