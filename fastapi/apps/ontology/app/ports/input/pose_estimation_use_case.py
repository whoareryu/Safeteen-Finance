from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.pose_estimation_dto import PoseEstimateCommand, PoseEstimateResult


class PoseEstimationUseCase(ABC):
    """Inbound 입력 포트 — ViTPose 기반 top-down 인체 키포인트 추정."""

    @abstractmethod
    def estimate(self, command: PoseEstimateCommand) -> PoseEstimateResult:
        """이미지와 사람 bbox 목록으로 인물별 키포인트·자세를 추정한다."""
        pass
