"""view_stat API schemas."""


from pydantic import BaseModel, Field


class ViewStatSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("조회수 집계", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "조회수 집계",
            }
        }
    }
