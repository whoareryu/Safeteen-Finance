from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.video_classification_dto import VideoClassifyCommand, VideoClassifyResult


class VideoClassificationUseCase(ABC):
    """Inbound 입력 포트 — VideoMAE 기반 동영상 행동 분류."""

    @abstractmethod
    def classify(self, command: VideoClassifyCommand) -> VideoClassifyResult:
        """동영상 전체 분류 결과와 슬라이딩 윈도우 구간별 분류 결과를 반환한다."""
        pass
