from __future__ import annotations

from ontology.app.dtos.video_classification_dto import VideoClassifyCommand, VideoClassifyResult
from ontology.app.ports.input.video_classification_use_case import VideoClassificationUseCase
from ontology.app.ports.output.video_classification_model_port import VideoClassificationModelPort


class VideoClassificationInteractor(VideoClassificationUseCase):
    """ontology 허브의 동영상 분류 캐퍼빌리티 — VideoMAE 등 비디오 백엔드를 감싼다."""

    def __init__(self, model: VideoClassificationModelPort) -> None:
        self._model = model

    def classify(self, command: VideoClassifyCommand) -> VideoClassifyResult:
        return self._model.classify(command.video, command.filename)
