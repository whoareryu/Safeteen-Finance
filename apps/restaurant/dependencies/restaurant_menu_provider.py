from functools import lru_cache

from restaurant.adapter.outbound.pg.restaurant_menu_pg_repository import RestaurantMenuPgRepository
from restaurant.app.ports.input.restaurant_menu_use_case import RestaurantMenuUseCase
from restaurant.app.ports.output.restaurant_menu_repository import RestaurantMenuRepository
from restaurant.app.use_cases.restaurant_menu_interactor import RestaurantMenuInteractor


@lru_cache
def get_restaurant_menu_use_case() -> RestaurantMenuUseCase:
    repository: RestaurantMenuRepository = RestaurantMenuPgRepository()
    return RestaurantMenuInteractor(repository=repository)
