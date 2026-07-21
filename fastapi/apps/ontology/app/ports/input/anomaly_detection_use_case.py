from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.anomaly_detection_dto import AnomalyDetectCommand, AnomalyDetectResult


class AnomalyDetectionUseCase(ABC):
    """Inbound 입력 포트 — WinCLIP(CLIP zero-shot) 기반 이상 화상 탐지."""

    @abstractmethod
    def detect(self, command: AnomalyDetectCommand) -> AnomalyDetectResult:
        """이미지와 결함 유형 텍스트 프롬프트로 이상 여부·점수를 반환한다."""
        pass
