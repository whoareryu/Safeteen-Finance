from functools import lru_cache

from gourmet.adapter.outbound.pg.view_stat_pg_repository import ViewStatPgRepository
from gourmet.app.ports.input.view_stat_use_case import ViewStatUseCase
from gourmet.app.ports.output.view_stat_repository import ViewStatRepository
from gourmet.app.use_cases.view_stat_interactor import ViewStatInteractor


@lru_cache
def get_view_stat_use_case() -> ViewStatUseCase:
    repository: ViewStatRepository = ViewStatPgRepository()
    return ViewStatInteractor(repository=repository)
