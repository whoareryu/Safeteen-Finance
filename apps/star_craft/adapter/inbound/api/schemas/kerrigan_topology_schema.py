from pydantic import BaseModel, Field


class TopologyQuerySchema(BaseModel):
    spoke_name: str | None = Field(None, description="특정 스포크 이름 (None = 전체 조회)")

    model_config = {"json_schema_extra": {"example": {"spoke_name": None}}}


class SpokeInfoSchema(BaseModel):
    name: str
    prefix: str
    status: str

    model_config = {
        "json_schema_extra": {
            "example": {"name": "titanic", "prefix": "/api/titanic", "status": "active"}
        }
    }


class TopologyResponseSchema(BaseModel):
    spokes: list[SpokeInfoSchema]
    total: int
