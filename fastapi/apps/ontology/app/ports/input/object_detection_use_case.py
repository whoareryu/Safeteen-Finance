from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.object_detection_dto import ObjectDetectCommand, ObjectDetectResult


class ObjectDetectionUseCase(ABC):
    """Inbound 입력 포트 — RT-DETR 기반 물체 감지(바운딩박스+클래스+신뢰도)."""

    @abstractmethod
    def detect(self, command: ObjectDetectCommand) -> ObjectDetectResult:
        """업로드된 이미지에서 물체를 감지해 바운딩박스 목록을 반환한다."""
        pass
