import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ontology.adapter.inbound.api.schemas.anomaly_detection_schema import AnomalyDetectResponse
from ontology.app.dtos.anomaly_detection_dto import AnomalyDetectCommand
from ontology.app.ports.input.anomaly_detection_use_case import AnomalyDetectionUseCase
from ontology.dependencies.anomaly_detection_provider import get_anomaly_detection_use_case

_MAX_ANOMALY_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_ANOMALY_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

anomaly_router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@anomaly_router.post(
    "/detect",
    response_model=AnomalyDetectResponse,
    responses={400: {"description": "지원하지 않는 포맷/결함 유형 누락"}, 413: {"description": "파일 크기 초과"}},
    summary="WinCLIP(CLIP zero-shot)으로 이상 화상 탐지 — 정상 샘플 학습 없이 텍스트 프롬프트로 결함 유형 지정",
)
async def detect_anomaly(
    file: UploadFile = File(...),
    defect_types: str = Query("crack,scratch,discoloration", description="쉼표로 구분한 결함 유형 목록"),
    threshold: float = Query(0.5, ge=0.0, le=1.0, description="이상 판정 임계값 (0~1)"),
    use_case: AnomalyDetectionUseCase = Depends(get_anomaly_detection_use_case),
) -> AnomalyDetectResponse:
    if file.content_type not in _ALLOWED_ANOMALY_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")

    content = await file.read()
    if len(content) > _MAX_ANOMALY_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")

    types = [t.strip() for t in defect_types.split(",") if t.strip()]

    try:
        result = await asyncio.to_thread(
            use_case.detect,
            AnomalyDetectCommand(image=content, defect_types=types, threshold=threshold),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return AnomalyDetectResponse(
        is_anomaly=result.is_anomaly,
        anomaly_score=result.anomaly_score,
        defect_category=result.defect_category,
        defect_scores=[{"defect_type": d.defect_type, "score": d.score} for d in result.defect_scores],
    )
