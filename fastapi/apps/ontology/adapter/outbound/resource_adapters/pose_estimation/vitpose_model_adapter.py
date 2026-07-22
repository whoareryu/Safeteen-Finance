from __future__ import annotations

import io
import logging

import torch
from PIL import Image, UnidentifiedImageError
from transformers import VitPoseForPoseEstimation, VitPoseImageProcessor

from ontology.app.dtos.object_detection_dto import BoundingBox
from ontology.app.dtos.pose_estimation_dto import DetectedPose, Keypoint
from ontology.app.ports.output.pose_estimation_model_port import PoseEstimationModelPort

logger = logging.getLogger(__name__)

_SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

# COCO 17 키포인트 순서 (pose-estimation.md §3-4)
_COCO_KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]


class VitPoseModelAdapter(PoseEstimationModelPort):
    """ViTPose-B(top-down) 기반 인체 키포인트 추정 어댑터. 사람 bbox가 있어야 동작한다."""

    def __init__(self, model_id: str = "usyd-community/vitpose-base-simple", device: str = "cpu") -> None:
        self._device = torch.device(device)
        self._processor = VitPoseImageProcessor.from_pretrained(model_id)
        self._model = VitPoseForPoseEstimation.from_pretrained(model_id).to(self._device)
        self._model.eval()
        logger.info("ViTPose 자세 추정 모델 로드 완료: %s (device=%s)", model_id, device)

    @torch.no_grad()
    def estimate(self, image_bytes: bytes, person_boxes: list[BoundingBox]) -> list[DetectedPose]:
        if not person_boxes:
            return []

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_format = image.format
            image = image.convert("RGB")
        except UnidentifiedImageError as e:
            raise ValueError("이미지로 인식할 수 없는 파일입니다.") from e

        if image_format not in _SUPPORTED_FORMATS:
            raise ValueError(f"지원하지 않는 이미지 포맷입니다: {image_format}")

        # VitPoseImageProcessor는 bbox를 COCO 포맷(x, y, w, h)으로 받는다.
        boxes_xywh = [[box.x, box.y, box.w, box.h] for box in person_boxes]
        inputs = self._processor(image, boxes=[boxes_xywh], return_tensors="pt").to(self._device)
        outputs = self._model(**inputs)
        pose_results = self._processor.post_process_pose_estimation(outputs, boxes=[boxes_xywh])[0]

        detected: list[DetectedPose] = []
        for person_box, result in zip(person_boxes, pose_results):
            keypoints = [
                Keypoint(
                    name=_COCO_KEYPOINT_NAMES[int(label)],
                    x=round(float(point[0]), 2),
                    y=round(float(point[1]), 2),
                    confidence=round(float(score), 4),
                )
                for point, score, label in zip(
                    result["keypoints"], result["scores"], result["labels"]
                )
            ]
            detected.append(DetectedPose(keypoints=keypoints, box=person_box))
        return detected
