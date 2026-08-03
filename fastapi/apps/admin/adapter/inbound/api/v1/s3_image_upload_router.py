from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from admin.adapter.inbound.mappers.s3_image_upload_mapper import to_response
from admin.adapter.inbound.api.schemas.s3_image_upload_schema import ImageUploadResponseSchema
from admin.app.dtos.s3_image_upload_dto import ImageUploadCommand
from admin.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from admin.dependencies.s3_image_upload_provider import get_s3_image_upload_use_case

s3_image_upload_router = APIRouter(prefix="/s3", tags=["s3-image-upload"])

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@s3_image_upload_router.post("/images", summary="이미지를 S3에 업로드하고 URL을 반환")
async def upload_image(
    file: UploadFile = File(...),
    use_case: S3ImageUploadUseCase = Depends(get_s3_image_upload_use_case),
) -> ImageUploadResponseSchema:
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail=f"이미지 파일만 업로드할 수 있습니다: {file.content_type}")
    data = await file.read()
    if len(data) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 10MB를 초과했습니다.")
    command = ImageUploadCommand(
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    result = await use_case.upload(command)
    return to_response(result)
