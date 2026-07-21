import asyncio
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ontology.adapter.inbound.api.schemas.pose_estimation_schema import PoseEstimateResponse
from ontology.app.dtos.object_detection_dto import BoundingBox
from ontology.app.dtos.pose_estimation_dto import PoseEstimateCommand
from ontology.app.ports.input.pose_estimation_use_case import PoseEstimationUseCase
from ontology.dependencies.pose_estimation_provider import get_pose_estimation_use_case

_MAX_POSE_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_POSE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

pose_router = APIRouter(prefix="/pose", tags=["pose"])


@pose_router.post(
    "/estimate",
    response_model=PoseEstimateResponse,
    responses={400: {"description": "지원하지 않는 포맷/person_boxes 형식 오류"}, 413: {"description": "파일 크기 초과"}},
    summary="ViTPose로 인물 키포인트·자세 추정 (top-down — /detection/detect 결과의 person bbox 필요)",
)
async def estimate_pose(
    file: UploadFile = File(...),
    person_boxes: str = Form(
        ..., description='감지된 사람 bbox JSON 배열: [{"x":0,"y":0,"w":0,"h":0}, ...]'
    ),
    use_case: PoseEstimationUseCase = Depends(get_pose_estimation_use_case),
) -> PoseEstimateResponse:
    if file.content_type not in _ALLOWED_POSE_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")

    content = await file.read()
    if len(content) > _MAX_POSE_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")

    try:
        raw_boxes = json.loads(person_boxes)
        boxes = [BoundingBox(x=b["x"], y=b["y"], w=b["w"], h=b["h"]) for b in raw_boxes]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise HTTPException(status_code=400, detail="person_boxes 형식이 올바르지 않습니다.") from e

    try:
        result = await asyncio.to_thread(
            use_case.estimate, PoseEstimateCommand(image=content, person_boxes=boxes)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return PoseEstimateResponse(
        people=[
            {
                "keypoints": [
                    {"name": kp.name, "x": kp.x, "y": kp.y, "confidence": kp.confidence}
                    for kp in person.keypoints
                ],
                "box": {"x": person.box.x, "y": person.box.y, "w": person.box.w, "h": person.box.h},
                "pose_category": person.pose_category,
            }
            for person in result.people
        ]
    )
