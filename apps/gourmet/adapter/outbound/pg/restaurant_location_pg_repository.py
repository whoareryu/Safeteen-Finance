from __future__ import annotations

from gourmet.app.ports.output.restaurant_location_repository import RestaurantLocationRepository


class RestaurantLocationPgRepository(RestaurantLocationRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
