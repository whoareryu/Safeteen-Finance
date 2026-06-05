from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_location_pg_repository import RestaurantLocationPgRepository
from gourmet.app.ports.input.restaurant_location_use_case import RestaurantLocationUseCase
from gourmet.app.ports.output.restaurant_location_repository import RestaurantLocationRepository
from gourmet.app.use_cases.restaurant_location_interactor import RestaurantLocationInteractor


@lru_cache
def get_restaurant_location_use_case() -> RestaurantLocationUseCase:
    repository: RestaurantLocationRepository = RestaurantLocationPgRepository()
    return RestaurantLocationInteractor(repository=repository)
