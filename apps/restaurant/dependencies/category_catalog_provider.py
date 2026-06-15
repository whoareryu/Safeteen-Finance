from functools import lru_cache

from restaurant.adapter.outbound.pg.category_catalog_pg_repository import CategoryCatalogPgRepository
from restaurant.app.ports.input.category_catalog_use_case import CategoryCatalogUseCase
from restaurant.app.ports.output.category_catalog_repository import CategoryCatalogRepository
from restaurant.app.use_cases.category_catalog_interactor import CategoryCatalogInteractor


@lru_cache
def get_category_catalog_use_case() -> CategoryCatalogUseCase:
    repository: CategoryCatalogRepository = CategoryCatalogPgRepository()
    return CategoryCatalogInteractor(repository=repository)
