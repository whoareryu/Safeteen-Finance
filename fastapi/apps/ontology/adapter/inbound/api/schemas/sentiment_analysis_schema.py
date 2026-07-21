from pydantic import BaseModel, Field


class SentimentAnalyzeRequest(BaseModel):

    text: str = Field(..., min_length=1, max_length=2000, description="감정을 분석할 텍스트")


class SentimentScoreSchema(BaseModel):

    label: str
    score: float


class SentimentAnalyzeResponse(BaseModel):

    sentiment: str = Field(..., description="가장 확률이 높은 감정 클래스")
    confidence: float = Field(..., description="sentiment 클래스의 확률")
    scores: list[SentimentScoreSchema] = Field(..., description="전체 클래스별 확률")
