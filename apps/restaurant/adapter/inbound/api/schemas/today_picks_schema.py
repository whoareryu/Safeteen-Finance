"""today_picks API schemas."""


from pydantic import BaseModel, Field


class TodayPicksSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("오늘의 추천 목록", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "오늘의 추천 목록",
            }
        }
    }
