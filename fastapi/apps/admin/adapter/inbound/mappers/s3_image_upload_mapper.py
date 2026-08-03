from __future__ import annotations

from admin.adapter.inbound.api.schemas.s3_image_upload_schema import ImageUploadResponseSchema
from admin.app.dtos.s3_image_upload_dto import ImageUploadResult


def to_response(result: ImageUploadResult) -> ImageUploadResponseSchema:
    return ImageUploadResponseSchema(url=result.url)
