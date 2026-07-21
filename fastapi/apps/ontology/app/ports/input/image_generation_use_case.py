from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.image_generation_dto import ImageGenerateCommand, ImageGenerateResult


class ImageGenerationUseCase(ABC):
    """Inbound 입력 포트 — 텍스트 프롬프트 기반 이미지 생성 (SDXL Turbo 등)."""

    @abstractmethod
    async def generate(self, command: ImageGenerateCommand) -> ImageGenerateResult:
        """프롬프트로 이미지를 생성해 저장하고, 접근 가능한 URL과 메타데이터를 반환한다."""
        pass
