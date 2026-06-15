from functools import lru_cache

from restaurant.adapter.outbound.pg.restaurant_enrichment_pg_repository import RestaurantEnrichmentPgRepository
from restaurant.app.ports.input.restaurant_enrichment_use_case import RestaurantEnrichmentUseCase
from restaurant.app.ports.output.restaurant_enrichment_repository import RestaurantEnrichmentRepository
from restaurant.app.use_cases.restaurant_enrichment_interactor import RestaurantEnrichmentInteractor


@lru_cache
def get_restaurant_enrichment_use_case() -> RestaurantEnrichmentUseCase:
    repository: RestaurantEnrichmentRepository = RestaurantEnrichmentPgRepository()
    return RestaurantEnrichmentInteractor(repository=repository)
