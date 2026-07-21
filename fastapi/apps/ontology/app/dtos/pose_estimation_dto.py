from dataclasses import dataclass

from ontology.app.dtos.object_detection_dto import BoundingBox


@dataclass(frozen=True)
class Keypoint:

    name: str
    x: float
    y: float
    confidence: float


@dataclass(frozen=True)
class DetectedPose:
    """모델이 반환하는 원시 추정 결과 — 자세 분류 전."""

    keypoints: list[Keypoint]
    box: BoundingBox


@dataclass(frozen=True)
class PersonPose:

    keypoints: list[Keypoint]
    box: BoundingBox
    pose_category: str


@dataclass(frozen=True)
class PoseEstimateCommand:

    image: bytes
    # Top-down 방식이라 상류(detection_agent)에서 감지한 사람 bbox가 필요하다.
    person_boxes: list[BoundingBox]


@dataclass(frozen=True)
class PoseEstimateResult:

    people: list[PersonPose]
