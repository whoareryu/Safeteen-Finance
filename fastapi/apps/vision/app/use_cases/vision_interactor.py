from __future__ import annotations

from dataclasses import replace

from vision.adapter.inbound.api.schemas.vision_schema import VisionSchema
from vision.app.dtos.vision_dto import (
    VisionImageQuery,
    VisionImageResponse,
    VisionQuery,
    VisionResponse,
)
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.app.ports.output.image_storage_gateway import ImageStorageGateway
from vision.app.ports.output.vision_port import VisionPort


class VisionInteractor(VisionUseCase):

    def __init__(self, repository: VisionPort, storage: ImageStorageGateway):
        self.repository = repository
        self.storage = storage

    async def introduce_myself(self, schema) -> VisionResponse:
        schema = VisionSchema(id=1, name="Vision")
        return VisionResponse(id=schema.id, name=schema.name)

    async def process_image(self, schema: VisionImageQuery) -> VisionImageResponse:
        url = await self.storage.save(schema.filename, schema.content_type, schema.data)
        response = await self.repository.process_image(schema)
        return replace(response, url=url)
