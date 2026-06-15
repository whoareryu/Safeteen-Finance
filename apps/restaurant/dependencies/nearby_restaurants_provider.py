from functools import lru_cache

from restaurant.adapter.outbound.pg.nearby_restaurants_pg_repository import NearbyRestaurantsPgRepository
from restaurant.app.ports.input.nearby_restaurants_use_case import NearbyRestaurantsUseCase
from restaurant.app.ports.output.nearby_restaurants_repository import NearbyRestaurantsRepository
from restaurant.app.use_cases.nearby_restaurants_interactor import NearbyRestaurantsInteractor


@lru_cache
def get_nearby_restaurants_use_case() -> NearbyRestaurantsUseCase:
    repository: NearbyRestaurantsRepository = NearbyRestaurantsPgRepository()
    return NearbyRestaurantsInteractor(repository=repository)
