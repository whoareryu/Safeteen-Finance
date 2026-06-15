from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.topic_restaurants_schema import TopicRestaurantsSchema
from restaurant.app.dtos.topic_restaurants_dto import TopicRestaurantsResponse
from restaurant.app.ports.input.topic_restaurants_use_case import TopicRestaurantsUseCase
from restaurant.dependencies.topic_restaurants_provider import get_topic_restaurants_use_case

topic_restaurants_router = APIRouter(prefix="/gourmet", tags=["gourmet-topic_restaurants"])
router = topic_restaurants_router


@topic_restaurants_router.get("/myself")
async def introduce_myself(
    use_case: TopicRestaurantsUseCase = Depends(get_topic_restaurants_use_case),
) -> TopicRestaurantsResponse:
    return await use_case.introduce_myself(TopicRestaurantsSchema(id=1, name="주제별 맛집"))
