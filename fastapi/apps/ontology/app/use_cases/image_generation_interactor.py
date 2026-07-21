from __future__ import annotations

import asyncio
import uuid

from ontology.app.dtos.image_generation_dto import ImageGenerateCommand, ImageGenerateResult
from ontology.app.ports.input.image_generation_use_case import ImageGenerationUseCase
from ontology.app.ports.output.image_generation_model_port import ImageGenerationModelPort
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway


class ImageGenerationInteractor(ImageGenerationUseCase):
    """ontology 허브의 이미지 생성 캐퍼빌리티 — SDXL Turbo 등 diffusion 백엔드를 감싼다."""

    def __init__(self, model: ImageGenerationModelPort, storage: ImageStorageGateway) -> None:
        self._model = model
        self._storage = storage

    async def generate(self, command: ImageGenerateCommand) -> ImageGenerateResult:
        # 생성은 CPU/GPU-bound 장시간 작업이므로 이벤트 루프를 막지 않도록 스레드로 위임한다.
        image_bytes, seed = await asyncio.to_thread(self._model.generate, command)
        filename = f"{uuid.uuid4().hex}.png"
        url = await self._storage.save(filename, "image/png", image_bytes)
        return ImageGenerateResult(
            image_url=url,
            seed=seed,
            steps=command.num_inference_steps,
            model=self._model.model_name(),
        )
