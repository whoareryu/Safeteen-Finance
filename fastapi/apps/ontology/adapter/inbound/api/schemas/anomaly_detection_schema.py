from pydantic import BaseModel, Field


class DefectScoreSchema(BaseModel):

    defect_type: str
    score: float = Field(..., description="0~1, 0.5 초과면 해당 결함 유형에 가까움")


class AnomalyDetectResponse(BaseModel):

    is_anomaly: bool
    anomaly_score: float = Field(..., description="가장 유력한 결함 유형의 점수 (0~1)")
    defect_category: str = Field(..., description="가장 유력한 결함 유형, 정상이면 'normal'")
    defect_scores: list[DefectScoreSchema] = Field(..., description="결함 유형별 점수")
