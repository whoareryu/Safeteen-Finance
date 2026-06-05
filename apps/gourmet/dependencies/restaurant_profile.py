from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_profile_pg_repository import RestaurantProfilePgRepository
from gourmet.app.ports.input.restaurant_profile_use_case import RestaurantProfileUseCase
from gourmet.app.ports.output.restaurant_profile_repository import RestaurantProfileRepository
from gourmet.app.use_cases.restaurant_profile_interactor import RestaurantProfileInteractor


@lru_cache
def get_restaurant_profile_use_case() -> RestaurantProfileUseCase:
    repository: RestaurantProfileRepository = RestaurantProfilePgRepository()
    return RestaurantProfileInteractor(repository=repository)
