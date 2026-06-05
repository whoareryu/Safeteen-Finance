from __future__ import annotations

from gourmet.app.ports.output.search_query_repository import SearchQueryRepository


class SearchQueryPgRepository(SearchQueryRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
