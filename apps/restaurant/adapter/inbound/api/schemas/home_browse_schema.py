"""home_browse API schemas."""


from pydantic import BaseModel, Field


class HomeBrowseSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("홈 피드", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "홈 피드",
            }
        }
    }
