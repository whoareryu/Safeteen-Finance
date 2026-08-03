from __future__ import annotations

from admin.app.dtos.s3_image_upload_dto import ImageUploadCommand, ImageUploadResult
from admin.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway


class S3ImageUploadInteractor(S3ImageUploadUseCase):

    def __init__(self, storage: ImageStorageGateway) -> None:
        self._storage = storage

    async def upload(self, command: ImageUploadCommand) -> ImageUploadResult:
        url = await self._storage.save(command.filename, command.content_type, command.data)
        return ImageUploadResult(url=url)
