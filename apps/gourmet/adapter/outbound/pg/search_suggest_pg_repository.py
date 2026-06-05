from __future__ import annotations

from gourmet.app.ports.output.search_suggest_repository import SearchSuggestRepository


class SearchSuggestPgRepository(SearchSuggestRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
