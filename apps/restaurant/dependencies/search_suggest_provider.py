from functools import lru_cache

from restaurant.adapter.outbound.pg.search_suggest_pg_repository import SearchSuggestPgRepository
from restaurant.app.ports.input.search_suggest_use_case import SearchSuggestUseCase
from restaurant.app.ports.output.search_suggest_repository import SearchSuggestRepository
from restaurant.app.use_cases.search_suggest_interactor import SearchSuggestInteractor


@lru_cache
def get_search_suggest_use_case() -> SearchSuggestUseCase:
    repository: SearchSuggestRepository = SearchSuggestPgRepository()
    return SearchSuggestInteractor(repository=repository)
