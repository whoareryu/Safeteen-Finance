from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.yolo_dto import YoloTrainCommand, YoloTrainResult


class YoloUseCase(ABC):
    """Inbound 입력 포트 — 사람 얼굴 인식(분류) YOLO 파인튜닝.

    예측(predict)은 통합 이미지 분류 파이프라인(ImageClassifierUseCase, backend="yolo")으로
    이전됐다 — adapter/outbound/resource_adapters/image_classifier/yolo_classifier_model_adapter.py
    """

    @abstractmethod
    def execute(self, command: YoloTrainCommand) -> YoloTrainResult:
        """데이터셋을 로드하여 YOLO 분류 모델을 파인튜닝한다."""
        pass
