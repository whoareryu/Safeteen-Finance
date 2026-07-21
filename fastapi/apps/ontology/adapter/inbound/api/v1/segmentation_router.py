from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ontology.adapter.inbound.api.schemas.semantic_segmentation_schema import SegmentResponse
from ontology.app.dtos.semantic_segmentation_dto import SegmentCommand
from ontology.app.ports.input.semantic_segmentation_use_case import SemanticSegmentationUseCase
from ontology.dependencies.semantic_segmentation_provider import (
    get_semantic_segmentation_use_case,
)

_MAX_SEGMENT_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_SEGMENT_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

segmentation_router = APIRouter(prefix="/segmentation", tags=["segmentation"])


@segmentation_router.post(
    "/segment",
    response_model=SegmentResponse,
    responses={400: {"description": "지원하지 않는 포맷"}, 413: {"description": "파일 크기 초과"}},
    summary="SegFormer로 픽셀 단위 시멘틱 분할 (클래스별 면적 비율 + 오버레이 이미지)",
)
async def segment_image(
    file: UploadFile = File(...),
    use_case: SemanticSegmentationUseCase = Depends(get_semantic_segmentation_use_case),
) -> SegmentResponse:
    if file.content_type not in _ALLOWED_SEGMENT_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")

    content = await file.read()
    if len(content) > _MAX_SEGMENT_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")

    try:
        result = await use_case.segment(SegmentCommand(image=content))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return SegmentResponse(
        class_areas=[{"label": a.label, "ratio": a.ratio} for a in result.class_areas],
        overlay_image_url=result.overlay_image_url,
    )
