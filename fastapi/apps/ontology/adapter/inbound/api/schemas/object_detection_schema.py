from pydantic import BaseModel, Field


class BoundingBoxSchema(BaseModel):

    x: float
    y: float
    w: float
    h: float


class DetectedObjectSchema(BaseModel):

    label: str
    confidence: float
    box: BoundingBoxSchema


class ObjectDetectResponse(BaseModel):

    objects: list[DetectedObjectSchema] = Field(..., description="감지된 물체 목록")
    instance_count: int = Field(..., description="감지된 물체 총 개수")
