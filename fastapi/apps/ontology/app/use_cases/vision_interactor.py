from __future__ import annotations

from dataclasses import replace

from ontology.adapter.inbound.api.schemas.vision_schema import VisionSchema
from ontology.app.dtos.vision_dto import (
    VisionImageQuery,
    VisionImageResponse,
    VisionQuery,
    VisionResponse,
)
from ontology.app.ports.input.vision_use_case import VisionUseCase
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.app.ports.output.vision_port import VisionPort


class VisionInteractor(VisionUseCase):

    def __init__(self, repository: VisionPort, storage: ImageStorageGateway):
        self.repository = repository
        self.storage = storage

    async def introduce_myself(self, schema) -> VisionResponse:
        schema = VisionSchema(id=1, name="Vision")
        return VisionResponse(id=schema.id, name=schema.name)

    async def process_image(self, schema: VisionImageQuery) -> VisionImageResponse:
        url = await self.storage.save(schema.filename, schema.content_type, schema.data)
        # 버킷이 Block Public Access라 save()가 돌려준 URL 그대로는 열람 시 403이 난다.
        viewable_url = await self.storage.presigned_url(url)
        response = await self.repository.process_image(schema)
        return replace(response, url=viewable_url)
