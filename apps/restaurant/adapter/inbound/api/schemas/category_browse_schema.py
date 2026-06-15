"""category_browse API schemas."""


from pydantic import BaseModel, Field


class CategoryBrowseSchema(BaseModel):
    id: int = Field(0, description="서비스 ID")
    name: str = Field("카테고리 탐색", description="서비스명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "카테고리 탐색",
            }
        }
    }
