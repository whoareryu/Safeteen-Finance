from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.object_detection_dto import BoundingBox
from ontology.app.dtos.pose_estimation_dto import DetectedPose


class PoseEstimationModelPort(ABC):

    @abstractmethod
    def estimate(self, image_bytes: bytes, person_boxes: list[BoundingBox]) -> list[DetectedPose]:
        """이미지 bytes와 사람 bbox 목록으로 인물별 키포인트를 추정한다(자세 분류 전)."""
        pass
