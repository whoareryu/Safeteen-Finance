from functools import lru_cache

from gourmet.adapter.outbound.pg.home_browse_pg_repository import HomeBrowsePgRepository
from gourmet.app.ports.input.home_browse_use_case import HomeBrowseUseCase
from gourmet.app.ports.output.home_browse_repository import HomeBrowseRepository
from gourmet.app.use_cases.home_browse_interactor import HomeBrowseInteractor


@lru_cache
def get_home_browse_use_case() -> HomeBrowseUseCase:
    repository: HomeBrowseRepository = HomeBrowsePgRepository()
    return HomeBrowseInteractor(repository=repository)
