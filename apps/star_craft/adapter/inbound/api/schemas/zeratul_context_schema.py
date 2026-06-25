from pydantic import BaseModel, Field


class ContextQuerySchema(BaseModel):
    intent: str = Field(..., description="사용자 의도 요약")
    payload: str = Field("", description="원본 입력 텍스트")

    model_config = {
        "json_schema_extra": {"example": {"intent": "맛집 추천", "payload": "강남 맛집 알려줘"}}
    }


class ContextRouteResponseSchema(BaseModel):
    target_spoke: str
    confidence: float
    reason: str
