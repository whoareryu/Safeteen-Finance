from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.topic_restaurants_schema import TopicRestaurantsSchema
from restaurant.app.dtos.topic_restaurants_dto import TopicRestaurantsResponse


class TopicRestaurantsUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: TopicRestaurantsSchema) -> TopicRestaurantsResponse:
        pass
