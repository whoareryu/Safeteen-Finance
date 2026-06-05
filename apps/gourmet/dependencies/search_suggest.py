from functools import lru_cache

from gourmet.adapter.outbound.pg.search_suggest_pg_repository import SearchSuggestPgRepository
from gourmet.app.ports.input.search_suggest_use_case import SearchSuggestUseCase
from gourmet.app.ports.output.search_suggest_repository import SearchSuggestRepository
from gourmet.app.use_cases.search_suggest_interactor import SearchSuggestInteractor


@lru_cache
def get_search_suggest_use_case() -> SearchSuggestUseCase:
    repository: SearchSuggestRepository = SearchSuggestPgRepository()
    return SearchSuggestInteractor(repository=repository)
