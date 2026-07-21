from __future__ import annotations

import pytest

from ontology.app.dtos.image_classifier_dto import ImageClassifyCommand, ImageClassifyResult
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.use_cases.image_classifier_interactor import ImageClassifierInteractor


class _FakeModelPort(ImageClassifierModelPort):
    def __init__(self, result: ImageClassifyResult) -> None:
        self._result = result
        self.received_bytes: bytes | None = None

    def predict(self, image_bytes: bytes) -> ImageClassifyResult:
        self.received_bytes = image_bytes
        return self._result


def test_predict_dispatches_to_requested_backend() -> None:
    convnext_port = _FakeModelPort(ImageClassifyResult(label="튤립", confidence=0.9))
    yolo_port = _FakeModelPort(ImageClassifyResult(label="ben_afflek", confidence=0.7))
    interactor = ImageClassifierInteractor(
        backend_factories={"convnext": lambda: convnext_port, "yolo": lambda: yolo_port}
    )

    result = interactor.predict(ImageClassifyCommand(image=b"fake-bytes", backend="yolo"))

    assert result.label == "ben_afflek"
    assert yolo_port.received_bytes == b"fake-bytes"
    assert convnext_port.received_bytes is None


def test_predict_defaults_to_convnext_backend() -> None:
    convnext_port = _FakeModelPort(ImageClassifyResult(label="장미", confidence=0.5))
    interactor = ImageClassifierInteractor(backend_factories={"convnext": lambda: convnext_port})

    result = interactor.predict(ImageClassifyCommand(image=b"fake-bytes"))

    assert result.label == "장미"


def test_predict_raises_value_error_for_unknown_backend() -> None:
    interactor = ImageClassifierInteractor(backend_factories={"convnext": lambda: None})

    with pytest.raises(ValueError):
        interactor.predict(ImageClassifyCommand(image=b"x", backend="unknown"))
