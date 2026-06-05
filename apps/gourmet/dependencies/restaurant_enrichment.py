from functools import lru_cache

from gourmet.adapter.outbound.pg.restaurant_enrichment_pg_repository import RestaurantEnrichmentPgRepository
from gourmet.app.ports.input.restaurant_enrichment_use_case import RestaurantEnrichmentUseCase
from gourmet.app.ports.output.restaurant_enrichment_repository import RestaurantEnrichmentRepository
from gourmet.app.use_cases.restaurant_enrichment_interactor import RestaurantEnrichmentInteractor


@lru_cache
def get_restaurant_enrichment_use_case() -> RestaurantEnrichmentUseCase:
    repository: RestaurantEnrichmentRepository = RestaurantEnrichmentPgRepository()
    return RestaurantEnrichmentInteractor(repository=repository)
