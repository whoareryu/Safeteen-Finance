from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.image_classifier_dto import ImageClassifyResult


class ImageClassifierModelPort(ABC):
    """분류 백엔드(ConvNeXt/YOLO 등) 공통 계약 — 전처리는 각 어댑터가 자기 모델에 맞게 책임진다."""

    @abstractmethod
    def predict(self, image_bytes: bytes) -> ImageClassifyResult:
        """원본 이미지 bytes를 받아 (label, confidence)를 반환한다."""
        pass
