from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.image_classifier_dto import ImageClassifyCommand, ImageClassifyResult


class ImageClassifierUseCase(ABC):
    """Inbound 입력 포트 — ConvNeXt Nano 기반 범용 이미지 분류."""

    @abstractmethod
    def predict(self, command: ImageClassifyCommand) -> ImageClassifyResult:
        """업로드된 이미지로 가장 유력한 클래스를 예측한다."""
        pass
