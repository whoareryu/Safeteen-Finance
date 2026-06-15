from functools import lru_cache

from restaurant.adapter.outbound.pg.home_browse_pg_repository import HomeBrowsePgRepository
from restaurant.app.ports.input.home_browse_use_case import HomeBrowseUseCase
from restaurant.app.ports.output.home_browse_repository import HomeBrowseRepository
from restaurant.app.use_cases.home_browse_interactor import HomeBrowseInteractor


@lru_cache
def get_home_browse_use_case() -> HomeBrowseUseCase:
    repository: HomeBrowseRepository = HomeBrowsePgRepository()
    return HomeBrowseInteractor(repository=repository)
