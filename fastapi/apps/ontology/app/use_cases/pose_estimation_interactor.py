from __future__ import annotations

import math

from ontology.app.dtos.pose_estimation_dto import (
    Keypoint,
    PersonPose,
    PoseEstimateCommand,
    PoseEstimateResult,
)
from ontology.app.ports.input.pose_estimation_use_case import PoseEstimationUseCase
from ontology.app.ports.output.pose_estimation_model_port import PoseEstimationModelPort

_Point = tuple[float, float]


def _calculate_angle(a: _Point, b: _Point, c: _Point) -> float:
    """b를 꼭짓점으로 하는 a-b-c 각도(degree)."""
    ab = (a[0] - b[0], a[1] - b[1])
    cb = (c[0] - b[0], c[1] - b[1])
    mag_ab = math.hypot(*ab)
    mag_cb = math.hypot(*cb)
    if mag_ab == 0 or mag_cb == 0:
        return 0.0
    cos_angle = max(-1.0, min(1.0, (ab[0] * cb[0] + ab[1] * cb[1]) / (mag_ab * mag_cb)))
    return math.degrees(math.acos(cos_angle))


def _classify_pose(keypoints: list[Keypoint]) -> str:
    """왼쪽 다리 키포인트로 자세를 분류한다 (규칙 기반, pose-estimation.md §5)."""
    by_name = {kp.name: kp for kp in keypoints}
    required = {"left_hip", "left_knee", "left_ankle"}
    if not required.issubset(by_name):
        return "unknown"

    hip, knee, ankle = by_name["left_hip"], by_name["left_knee"], by_name["left_ankle"]
    knee_angle = _calculate_angle((hip.x, hip.y), (knee.x, knee.y), (ankle.x, ankle.y))

    if knee_angle < 90:
        return "sitting"
    if hip.y > ankle.y:
        return "lying"
    return "standing"


class PoseEstimationInteractor(PoseEstimationUseCase):
    """ontology 허브의 자세 추정 캐퍼빌리티 — ViTPose 추론 + 규칙 기반 자세 분류."""

    def __init__(self, model: PoseEstimationModelPort) -> None:
        self._model = model

    def estimate(self, command: PoseEstimateCommand) -> PoseEstimateResult:
        detected = self._model.estimate(command.image, command.person_boxes)
        people = [
            PersonPose(
                keypoints=pose.keypoints,
                box=pose.box,
                pose_category=_classify_pose(pose.keypoints),
            )
            for pose in detected
        ]
        return PoseEstimateResult(people=people)
