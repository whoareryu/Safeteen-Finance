from pydantic import BaseModel, Field


class LabelScoreSchema(BaseModel):

    label: str
    score: float


class ClipSegmentSchema(BaseModel):

    start_sec: float
    end_sec: float
    label: str
    confidence: float


class VideoClassifyResponse(BaseModel):

    action_label: str = Field(..., description="영상 전체 기준 최상위 행동 레이블")
    confidence: float = Field(..., description="action_label의 확률")
    top_k_labels: list[LabelScoreSchema] = Field(..., description="상위 K개 후보 레이블")
    clip_segments: list[ClipSegmentSchema] = Field(
        ..., description="슬라이딩 윈도우로 나눈 구간별 분류 결과 (임계값 이상만 포함)"
    )
