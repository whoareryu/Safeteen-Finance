from functools import lru_cache

from restaurant.adapter.outbound.pg.search_query_pg_repository import SearchQueryPgRepository
from restaurant.app.ports.input.search_query_use_case import SearchQueryUseCase
from restaurant.app.ports.output.search_query_repository import SearchQueryRepository
from restaurant.app.use_cases.search_query_interactor import SearchQueryInteractor


@lru_cache
def get_search_query_use_case() -> SearchQueryUseCase:
    repository: SearchQueryRepository = SearchQueryPgRepository()
    return SearchQueryInteractor(repository=repository)
