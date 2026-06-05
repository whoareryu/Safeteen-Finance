from __future__ import annotations

from gourmet.app.ports.output.nearby_restaurants_repository import NearbyRestaurantsRepository


class NearbyRestaurantsPgRepository(NearbyRestaurantsRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
