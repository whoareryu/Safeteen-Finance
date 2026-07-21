from __future__ import annotations

from ontology.app.dtos.anomaly_detection_dto import AnomalyDetectCommand, AnomalyDetectResult
from ontology.app.ports.input.anomaly_detection_use_case import AnomalyDetectionUseCase
from ontology.app.ports.output.anomaly_detection_model_port import AnomalyDetectionModelPort


class AnomalyDetectionInteractor(AnomalyDetectionUseCase):
    """ontology 허브의 이상 탐지 캐퍼빌리티 — WinCLIP 등 zero-shot 백엔드를 감싼다."""

    def __init__(self, model: AnomalyDetectionModelPort) -> None:
        self._model = model

    def detect(self, command: AnomalyDetectCommand) -> AnomalyDetectResult:
        return self._model.detect(command.image, command.defect_types, command.threshold)
