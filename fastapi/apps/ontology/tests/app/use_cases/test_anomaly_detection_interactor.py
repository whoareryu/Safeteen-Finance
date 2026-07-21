from __future__ import annotations

from ontology.app.dtos.anomaly_detection_dto import (
    AnomalyDetectCommand,
    AnomalyDetectResult,
    DefectScore,
)
from ontology.app.ports.output.anomaly_detection_model_port import AnomalyDetectionModelPort
from ontology.app.use_cases.anomaly_detection_interactor import AnomalyDetectionInteractor


class _FakeModelPort(AnomalyDetectionModelPort):
    def __init__(self, result: AnomalyDetectResult) -> None:
        self._result = result
        self.received_bytes: bytes | None = None
        self.received_defect_types: list[str] | None = None
        self.received_threshold: float | None = None

    def detect(
        self, image_bytes: bytes, defect_types: list[str], threshold: float
    ) -> AnomalyDetectResult:
        self.received_bytes = image_bytes
        self.received_defect_types = defect_types
        self.received_threshold = threshold
        return self._result


def test_detect_delegates_to_model_port() -> None:
    expected = AnomalyDetectResult(
        is_anomaly=True,
        anomaly_score=0.82,
        defect_category="crack",
        defect_scores=[DefectScore(defect_type="crack", score=0.82)],
    )
    model = _FakeModelPort(expected)
    interactor = AnomalyDetectionInteractor(model=model)

    result = interactor.detect(
        AnomalyDetectCommand(image=b"fake-bytes", defect_types=["crack"], threshold=0.6)
    )

    assert result is expected
    assert model.received_bytes == b"fake-bytes"
    assert model.received_defect_types == ["crack"]
    assert model.received_threshold == 0.6
