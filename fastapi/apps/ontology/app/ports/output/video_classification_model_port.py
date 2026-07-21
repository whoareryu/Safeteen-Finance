from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.video_classification_dto import VideoClassifyResult


class VideoClassificationModelPort(ABC):

    @abstractmethod
    def classify(self, video_bytes: bytes, filename: str) -> VideoClassifyResult:
        """동영상 bytes에서 프레임을 샘플링해 행동을 분류한다."""
        pass
