from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.anomaly_detection_dto import AnomalyDetectResult


class AnomalyDetectionModelPort(ABC):

    @abstractmethod
    def detect(
        self, image_bytes: bytes, defect_types: list[str], threshold: float
    ) -> AnomalyDetectResult:
        """이미지 bytes와 결함 유형 목록으로 CLIP zero-shot 이상 탐지를 수행한다."""
        pass
