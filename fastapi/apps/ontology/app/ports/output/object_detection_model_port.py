from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.object_detection_dto import ObjectDetectResult


class ObjectDetectionModelPort(ABC):

    @abstractmethod
    def detect(self, image_bytes: bytes, score_threshold: float) -> ObjectDetectResult:
        """이미지 bytes에서 물체를 감지한다."""
        pass
