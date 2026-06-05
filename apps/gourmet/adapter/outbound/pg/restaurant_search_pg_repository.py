from __future__ import annotations

from gourmet.app.ports.output.restaurant_search_repository import RestaurantSearchRepository


class RestaurantSearchPgRepository(RestaurantSearchRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
