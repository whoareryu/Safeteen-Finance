from fastapi import APIRouter, Depends, File, UploadFile

from vision.adapter.inbound.api.schemas.vision_schema import VisionSchema
from vision.app.dtos.vision_dto import VisionImageQuery, VisionImageResponse, VisionResponse
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.dependencies.vision_provider import get_vision_use_case

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
