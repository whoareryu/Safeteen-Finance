"""restaurant_domain API schemas."""

from restaurant.adapter.inbound.api.schemas.restaurant_schema import *  # noqa: F403


from pydantic import BaseModel, Field


class RestaurantDomainSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("맛집 도메인", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "맛집 도메인",
            }
        }
    }
