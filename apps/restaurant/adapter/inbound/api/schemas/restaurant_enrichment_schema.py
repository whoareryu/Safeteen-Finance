"""restaurant_enrichment API schemas."""

from restaurant.adapter.inbound.api.schemas.catalog_schema import *  # noqa: F403


from pydantic import BaseModel, Field


class RestaurantEnrichmentSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("맛집 보강", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "맛집 보강",
            }
        }
    }
