import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ontology.adapter.inbound.api.schemas.object_detection_schema import ObjectDetectResponse
from ontology.app.dtos.object_detection_dto import ObjectDetectCommand
from ontology.app.ports.input.object_detection_use_case import ObjectDetectionUseCase
from ontology.dependencies.object_detection_provider import get_object_detection_use_case

_MAX_DETECT_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_DETECT_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

detection_router = APIRouter(prefix="/detection", tags=["detection"])


@detection_router.post(
    "/detect",
    response_model=ObjectDetectResponse,
    responses={400: {"description": "지원하지 않는 포맷"}, 413: {"description": "파일 크기 초과"}},
    summary="RT-DETR로 이미지 내 물체 감지 (바운딩박스+클래스+신뢰도)",
)
async def detect_objects(
    file: UploadFile = File(...),
    score_threshold: float = Query(0.5, ge=0.0, le=1.0, description="신뢰도 임계값"),
    use_case: ObjectDetectionUseCase = Depends(get_object_detection_use_case),
) -> ObjectDetectResponse:
    if file.content_type not in _ALLOWED_DETECT_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")

    content = await file.read()
    if len(content) > _MAX_DETECT_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")

    try:
        result = await asyncio.to_thread(
            use_case.detect, ObjectDetectCommand(image=content, score_threshold=score_threshold)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ObjectDetectResponse(
        objects=[
            {
                "label": obj.label,
                "confidence": obj.confidence,
                "box": {"x": obj.box.x, "y": obj.box.y, "w": obj.box.w, "h": obj.box.h},
            }
            for obj in result.objects
        ],
        instance_count=result.instance_count,
    )
