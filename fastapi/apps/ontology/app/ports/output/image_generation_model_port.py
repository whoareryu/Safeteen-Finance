from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.image_generation_dto import ImageGenerateCommand


class ImageGenerationModelPort(ABC):

    @abstractmethod
    def generate(self, command: ImageGenerateCommand) -> tuple[bytes, int]:
        """프롬프트로 이미지를 생성해 (PNG bytes, seed)를 반환한다."""
        pass

    @abstractmethod
    def model_name(self) -> str:
        """생성에 사용된 모델 식별자(허깅페이스 ID 등)."""
        pass
