from functools import lru_cache

from gourmet.adapter.outbound.pg.search_query_pg_repository import SearchQueryPgRepository
from gourmet.app.ports.input.search_query_use_case import SearchQueryUseCase
from gourmet.app.ports.output.search_query_repository import SearchQueryRepository
from gourmet.app.use_cases.search_query_interactor import SearchQueryInteractor


@lru_cache
def get_search_query_use_case() -> SearchQueryUseCase:
    repository: SearchQueryRepository = SearchQueryPgRepository()
    return SearchQueryInteractor(repository=repository)
