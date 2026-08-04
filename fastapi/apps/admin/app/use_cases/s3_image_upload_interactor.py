from __future__ import annotations

from admin.app.dtos.s3_image_upload_dto import ImageUploadCommand, ImageUploadResult
from admin.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway


class S3ImageUploadInteractor(S3ImageUploadUseCase):

    def __init__(self, storage: ImageStorageGateway) -> None:
        self._storage = storage

    async def upload(self, command: ImageUploadCommand) -> ImageUploadResult:
        url = await self._storage.save(command.filename, command.content_type, command.data)
        # 버킷이 Block Public Access라 save()가 돌려준 URL 그대로는 열람 시 403이 난다.
        viewable_url = await self._storage.presigned_url(url)
        return ImageUploadResult(url=viewable_url)
