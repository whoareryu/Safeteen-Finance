"""restaurant_search API schemas."""


from pydantic import BaseModel, Field


class RestaurantSearchSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("맛집 검색", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "맛집 검색",
            }
        }
    }
