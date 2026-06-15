from __future__ import annotations

from restaurant.app.dtos.topic_restaurants_dto import TopicRestaurantsQuery, TopicRestaurantsResponse
from restaurant.app.ports.output.topic_restaurants_repository import TopicRestaurantsRepository


class TopicRestaurantsPgRepository(TopicRestaurantsRepository):
    async def introduce_myself(self, query: TopicRestaurantsQuery) -> TopicRestaurantsResponse:
        return TopicRestaurantsResponse(id=query.id, name=query.name)
