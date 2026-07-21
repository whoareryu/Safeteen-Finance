from pydantic import BaseModel, Field

from ontology.adapter.inbound.api.schemas.object_detection_schema import BoundingBoxSchema


class KeypointSchema(BaseModel):

    name: str
    x: float
    y: float
    confidence: float


class PersonPoseSchema(BaseModel):

    keypoints: list[KeypointSchema]
    box: BoundingBoxSchema
    pose_category: str = Field(..., description="standing | sitting | lying | unknown")


class PoseEstimateResponse(BaseModel):

    people: list[PersonPoseSchema] = Field(..., description="사람별 키포인트·자세 목록")
