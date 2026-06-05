from __future__ import annotations

from gourmet.app.ports.output.topic_restaurants_repository import TopicRestaurantsRepository


class TopicRestaurantsPgRepository(TopicRestaurantsRepository):
    """DB adapter — 구현은 interactor/service 로직에서 점진 이전."""

    pass
