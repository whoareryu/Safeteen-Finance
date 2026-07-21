from __future__ import annotations

from ontology.app.dtos.object_detection_dto import (
    BoundingBox,
    DetectedObject,
    ObjectDetectCommand,
    ObjectDetectResult,
)
from ontology.app.ports.output.object_detection_model_port import ObjectDetectionModelPort
from ontology.app.use_cases.object_detection_interactor import ObjectDetectionInteractor


class _FakeModelPort(ObjectDetectionModelPort):
    def __init__(self, result: ObjectDetectResult) -> None:
        self._result = result
        self.received_bytes: bytes | None = None
        self.received_threshold: float | None = None

    def detect(self, image_bytes: bytes, score_threshold: float) -> ObjectDetectResult:
        self.received_bytes = image_bytes
        self.received_threshold = score_threshold
        return self._result


def test_detect_delegates_to_model_port() -> None:
    expected = ObjectDetectResult(
        objects=[
            DetectedObject(label="cat", confidence=0.92, box=BoundingBox(x=10, y=20, w=30, h=40))
        ],
        instance_count=1,
    )
    model = _FakeModelPort(expected)
    interactor = ObjectDetectionInteractor(model=model)

    result = interactor.detect(ObjectDetectCommand(image=b"fake-bytes", score_threshold=0.6))

    assert result is expected
    assert model.received_bytes == b"fake-bytes"
    assert model.received_threshold == 0.6


def test_detect_returns_empty_when_no_objects_found() -> None:
    model = _FakeModelPort(ObjectDetectResult(objects=[], instance_count=0))
    interactor = ObjectDetectionInteractor(model=model)

    result = interactor.detect(ObjectDetectCommand(image=b"fake-bytes"))

    assert result.objects == []
    assert result.instance_count == 0
