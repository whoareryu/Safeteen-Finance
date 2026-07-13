from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.vision_dto import (
    VisionImageQuery,
    VisionImageResponse,
    VisionQuery,
    VisionResponse,
)


class VisionPort(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: VisionQuery) -> VisionResponse:
        pass

    @abstractmethod
    async def process_image(self, schema: VisionImageQuery) -> VisionImageResponse:
        pass
