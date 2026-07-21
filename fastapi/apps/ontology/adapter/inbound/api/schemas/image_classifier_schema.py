from pydantic import BaseModel, Field


class ImageClassifyResponse(BaseModel):

    label: str = Field(..., description="예측된 클래스 이름")
    confidence: float = Field(..., description="예측 확신도 (0~1)")
