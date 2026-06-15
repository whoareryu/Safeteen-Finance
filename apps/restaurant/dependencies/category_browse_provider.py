from functools import lru_cache

from restaurant.adapter.outbound.pg.category_browse_pg_repository import CategoryBrowsePgRepository
from restaurant.app.ports.input.category_browse_use_case import CategoryBrowseUseCase
from restaurant.app.ports.output.category_browse_repository import CategoryBrowseRepository
from restaurant.app.use_cases.category_browse_interactor import CategoryBrowseInteractor


@lru_cache
def get_category_browse_use_case() -> CategoryBrowseUseCase:
    repository: CategoryBrowseRepository = CategoryBrowsePgRepository()
    return CategoryBrowseInteractor(repository=repository)
