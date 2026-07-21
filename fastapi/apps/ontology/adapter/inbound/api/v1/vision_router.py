import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ontology.adapter.inbound.api.schemas.image_classifier_schema import ImageClassifyResponse
from ontology.adapter.inbound.api.schemas.vision_schema import VisionSchema
from ontology.adapter.inbound.api.schemas.yolo_schema import YoloTrainRequest, YoloTrainResponse
from ontology.app.dtos.image_classifier_dto import ImageClassifyCommand
from ontology.app.dtos.vision_dto import VisionImageQuery, VisionImageResponse, VisionResponse
from ontology.app.dtos.yolo_dto import YoloTrainCommand
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.app.ports.input.vision_use_case import VisionUseCase
from ontology.app.ports.input.yolo_use_case import YoloUseCase
from ontology.dependencies.image_classifier_provider import get_image_classifier_use_case
from ontology.dependencies.vision_provider import get_vision_use_case
from ontology.dependencies.yolo_provider import get_yolo_use_case

_MAX_CLASSIFY_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_CLASSIFY_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

vision_router = APIRouter(prefix="/vision", tags=["vision"])

@vision_router.get("/myself")
async def introduce_myself(
    vision: VisionUseCase = Depends(get_vision_use_case)
) -> VisionResponse:
    return await vision.introduce_myself(
        VisionSchema(id=1, name="Vision")
    )


@vision_router.post("/upload", summary="비전 처리용 이미지 업로드")
async def upload_image(
    file: UploadFile = File(...),
    vision: VisionUseCase = Depends(get_vision_use_case),
) -> VisionImageResponse:
    content = await file.read()
    return await vision.process_image(
        VisionImageQuery(
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            data=content,
        )
    )


@vision_router.post(
    "/yolo-train",
    response_model=YoloTrainResponse,
    summary="사람 얼굴 인식 YOLO 분류 모델 파인튜닝",
)
async def train_yolo(
    body: YoloTrainRequest,
    use_case: YoloUseCase = Depends(get_yolo_use_case),
) -> YoloTrainResponse:
    command = YoloTrainCommand(
        epochs=body.epochs,
        batch_size=body.batch_size,
        imgsz=body.imgsz,
        device=body.device,
    )
    # 학습은 CPU/GPU-bound 장시간 작업이므로 이벤트 루프를 막지 않도록 스레드로 위임한다.
    result = await asyncio.to_thread(use_case.execute, command)
    return YoloTrainResponse(
        dataset_root=result.dataset_root,
        epochs=result.epochs,
        classes=result.classes,
        weights_path=result.weights_path,
    )


@vision_router.post(
    "/classify",
    response_model=ImageClassifyResponse,
    responses={400: {"description": "지원하지 않는 포맷/backend"}, 413: {"description": "파일 크기 초과"}},
    summary="이미지 분류 — backend로 모델 선택 (convnext: 범용, yolo: 얼굴 인식)",
)
async def classify_image(
    file: UploadFile = File(...),
    backend: str = Query("convnext", description="분류 backend: convnext | yolo"),
    use_case: ImageClassifierUseCase = Depends(get_image_classifier_use_case),
) -> ImageClassifyResponse:
    if file.content_type not in _ALLOWED_CLASSIFY_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")

    content = await file.read()
    if len(content) > _MAX_CLASSIFY_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")

    try:
        result = await asyncio.to_thread(
            use_case.predict, ImageClassifyCommand(image=content, backend=backend)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ImageClassifyResponse(label=result.label, confidence=result.confidence)
