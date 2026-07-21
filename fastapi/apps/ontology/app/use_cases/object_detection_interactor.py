from __future__ import annotations

from ontology.app.dtos.object_detection_dto import ObjectDetectCommand, ObjectDetectResult
from ontology.app.ports.input.object_detection_use_case import ObjectDetectionUseCase
from ontology.app.ports.output.object_detection_model_port import ObjectDetectionModelPort


class ObjectDetectionInteractor(ObjectDetectionUseCase):
    """ontology 허브의 물체 감지 캐퍼빌리티 — RT-DETR 등 detection 백엔드를 감싼다."""

    def __init__(self, model: ObjectDetectionModelPort) -> None:
        self._model = model

    def detect(self, command: ObjectDetectCommand) -> ObjectDetectResult:
        return self._model.detect(command.image, command.score_threshold)
