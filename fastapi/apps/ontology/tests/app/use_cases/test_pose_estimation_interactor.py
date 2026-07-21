from __future__ import annotations

from ontology.app.dtos.object_detection_dto import BoundingBox
from ontology.app.dtos.pose_estimation_dto import DetectedPose, Keypoint, PoseEstimateCommand
from ontology.app.ports.output.pose_estimation_model_port import PoseEstimationModelPort
from ontology.app.use_cases.pose_estimation_interactor import PoseEstimationInteractor


class _FakeModelPort(PoseEstimationModelPort):
    def __init__(self, detected: list[DetectedPose]) -> None:
        self._detected = detected
        self.received_boxes: list[BoundingBox] | None = None

    def estimate(self, image_bytes: bytes, person_boxes: list[BoundingBox]) -> list[DetectedPose]:
        self.received_boxes = person_boxes
        return self._detected


def _keypoint(name: str, x: float, y: float) -> Keypoint:
    return Keypoint(name=name, x=x, y=y, confidence=0.9)


def test_estimate_classifies_standing_pose() -> None:
    box = BoundingBox(x=0, y=0, w=100, h=200)
    keypoints = [
        _keypoint("left_hip", 50, 100),
        _keypoint("left_knee", 50, 150),
        _keypoint("left_ankle", 50, 195),
    ]
    model = _FakeModelPort([DetectedPose(keypoints=keypoints, box=box)])
    interactor = PoseEstimationInteractor(model=model)

    result = interactor.estimate(PoseEstimateCommand(image=b"fake-bytes", person_boxes=[box]))

    assert len(result.people) == 1
    assert result.people[0].pose_category == "standing"
    assert model.received_boxes == [box]


def test_estimate_classifies_sitting_pose_from_bent_knee() -> None:
    box = BoundingBox(x=0, y=0, w=100, h=200)
    keypoints = [
        _keypoint("left_hip", 50, 100),
        _keypoint("left_knee", 70, 100),
        _keypoint("left_ankle", 50, 100),
    ]
    model = _FakeModelPort([DetectedPose(keypoints=keypoints, box=box)])
    interactor = PoseEstimationInteractor(model=model)

    result = interactor.estimate(PoseEstimateCommand(image=b"fake-bytes", person_boxes=[box]))

    assert result.people[0].pose_category == "sitting"


def test_estimate_returns_unknown_when_leg_keypoints_missing() -> None:
    box = BoundingBox(x=0, y=0, w=100, h=200)
    model = _FakeModelPort([DetectedPose(keypoints=[_keypoint("nose", 10, 10)], box=box)])
    interactor = PoseEstimationInteractor(model=model)

    result = interactor.estimate(PoseEstimateCommand(image=b"fake-bytes", person_boxes=[box]))

    assert result.people[0].pose_category == "unknown"
