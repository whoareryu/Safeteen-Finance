from functools import lru_cache

from restaurant.adapter.outbound.pg.restaurant_location_pg_repository import RestaurantLocationPgRepository
from restaurant.app.ports.input.restaurant_location_use_case import RestaurantLocationUseCase
from restaurant.app.ports.output.restaurant_location_repository import RestaurantLocationRepository
from restaurant.app.use_cases.restaurant_location_interactor import RestaurantLocationInteractor


@lru_cache
def get_restaurant_location_use_case() -> RestaurantLocationUseCase:
    repository: RestaurantLocationRepository = RestaurantLocationPgRepository()
    return RestaurantLocationInteractor(repository=repository)
