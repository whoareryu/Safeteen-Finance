from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_menu_pg_repository import RestaurantMenuPgRepository
from gourmet.app.ports.input.restaurant_menu_use_case import RestaurantMenuUseCase
from gourmet.app.ports.output.restaurant_menu_repository import RestaurantMenuRepository
from gourmet.app.use_cases.restaurant_menu_interactor import RestaurantMenuInteractor


@lru_cache
def get_restaurant_menu_use_case() -> RestaurantMenuUseCase:
    repository: RestaurantMenuRepository = RestaurantMenuPgRepository()
    return RestaurantMenuInteractor(repository=repository)
