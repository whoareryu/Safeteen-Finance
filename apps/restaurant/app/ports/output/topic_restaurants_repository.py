from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.topic_restaurants_dto import TopicRestaurantsQuery, TopicRestaurantsResponse


class TopicRestaurantsRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: TopicRestaurantsQuery) -> TopicRestaurantsResponse:
        pass
