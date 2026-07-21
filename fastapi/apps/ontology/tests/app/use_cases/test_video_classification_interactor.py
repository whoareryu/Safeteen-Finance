from __future__ import annotations

from ontology.app.dtos.video_classification_dto import (
    ClipSegment,
    LabelScore,
    VideoClassifyCommand,
    VideoClassifyResult,
)
from ontology.app.ports.output.video_classification_model_port import VideoClassificationModelPort
from ontology.app.use_cases.video_classification_interactor import VideoClassificationInteractor


class _FakeModelPort(VideoClassificationModelPort):
    def __init__(self, result: VideoClassifyResult) -> None:
        self._result = result
        self.received_video: bytes | None = None
        self.received_filename: str | None = None

    def classify(self, video_bytes: bytes, filename: str) -> VideoClassifyResult:
        self.received_video = video_bytes
        self.received_filename = filename
        return self._result


def test_classify_delegates_to_model_port() -> None:
    expected = VideoClassifyResult(
        action_label="달리기",
        confidence=0.88,
        top_k_labels=[LabelScore(label="달리기", score=0.88), LabelScore(label="걷기", score=0.1)],
        clip_segments=[
            ClipSegment(start_sec=0.0, end_sec=0.53, label="달리기", confidence=0.88)
        ],
    )
    model = _FakeModelPort(expected)
    interactor = VideoClassificationInteractor(model=model)

    result = interactor.classify(
        VideoClassifyCommand(video=b"fake-video-bytes", filename="clip.mp4")
    )

    assert result is expected
    assert model.received_video == b"fake-video-bytes"
    assert model.received_filename == "clip.mp4"
