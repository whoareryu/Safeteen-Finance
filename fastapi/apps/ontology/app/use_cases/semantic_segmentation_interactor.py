from __future__ import annotations

import asyncio
import uuid

from ontology.app.dtos.semantic_segmentation_dto import SegmentCommand, SegmentResult
from ontology.app.ports.input.semantic_segmentation_use_case import SemanticSegmentationUseCase
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.app.ports.output.semantic_segmentation_model_port import SemanticSegmentationModelPort


class SemanticSegmentationInteractor(SemanticSegmentationUseCase):
    """ontology 허브의 시멘틱 분할 캐퍼빌리티 — SegFormer 추론 + 오버레이 이미지 저장."""

    def __init__(
        self, model: SemanticSegmentationModelPort, storage: ImageStorageGateway
    ) -> None:
        self._model = model
        self._storage = storage

    async def segment(self, command: SegmentCommand) -> SegmentResult:
        # 분할 추론은 CPU/GPU-bound 장시간 작업이므로 이벤트 루프를 막지 않도록 스레드로 위임한다.
        output = await asyncio.to_thread(self._model.segment, command.image)
        filename = f"{uuid.uuid4().hex}.png"
        url = await self._storage.save(filename, "image/png", output.overlay_png)
        return SegmentResult(class_areas=output.class_areas, overlay_image_url=url)
