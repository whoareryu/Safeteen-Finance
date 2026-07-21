from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.semantic_segmentation_dto import SegmentCommand, SegmentResult


class SemanticSegmentationUseCase(ABC):
    """Inbound 입력 포트 — SegFormer 기반 픽셀 단위 시멘틱 분할."""

    @abstractmethod
    async def segment(self, command: SegmentCommand) -> SegmentResult:
        """이미지를 픽셀 단위로 분할해 클래스별 면적 비율과 오버레이 이미지 URL을 반환한다."""
        pass
