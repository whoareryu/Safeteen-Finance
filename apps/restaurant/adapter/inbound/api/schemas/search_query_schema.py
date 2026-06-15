"""search_query API schemas."""


from pydantic import BaseModel, Field


class SearchQuerySchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("검색 쿼리", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "검색 쿼리",
            }
        }
    }
