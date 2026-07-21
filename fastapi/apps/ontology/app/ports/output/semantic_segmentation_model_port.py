from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.semantic_segmentation_dto import SegmentModelOutput


class SemanticSegmentationModelPort(ABC):

    @abstractmethod
    def segment(self, image_bytes: bytes) -> SegmentModelOutput:
        """이미지를 픽셀 단위로 분할해 클래스별 면적 비율과 오버레이 PNG를 반환한다."""
        pass
