from functools import lru_cache

from restaurant.adapter.outbound.pg.restaurant_domain_pg_repository import RestaurantDomainPgRepository
from restaurant.app.ports.input.restaurant_domain_use_case import RestaurantDomainUseCase
from restaurant.app.ports.output.restaurant_domain_repository import RestaurantDomainRepository
from restaurant.app.use_cases.restaurant_domain_interactor import RestaurantDomainInteractor


@lru_cache
def get_restaurant_domain_use_case() -> RestaurantDomainUseCase:
    repository: RestaurantDomainRepository = RestaurantDomainPgRepository()
    return RestaurantDomainInteractor(repository=repository)
