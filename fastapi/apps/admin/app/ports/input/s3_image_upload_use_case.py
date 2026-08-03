from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.s3_image_upload_dto import ImageUploadCommand, ImageUploadResult


class S3ImageUploadUseCase(ABC):

    @abstractmethod
    async def upload(self, command: ImageUploadCommand) -> ImageUploadResult:
        """이미지를 S3에 올리고 접근 가능한 URL을 반환한다."""
        pass
