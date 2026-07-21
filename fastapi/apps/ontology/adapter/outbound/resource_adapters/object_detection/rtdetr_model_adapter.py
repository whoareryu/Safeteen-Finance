from __future__ import annotations

import io
import logging

import torch
from PIL import Image, UnidentifiedImageError
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor

from ontology.app.dtos.object_detection_dto import BoundingBox, DetectedObject, ObjectDetectResult
from ontology.app.ports.output.object_detection_model_port import ObjectDetectionModelPort

logger = logging.getLogger(__name__)

_SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


class RtDetrModelAdapter(ObjectDetectionModelPort):
    """RT-DETR(Real-Time Detection Transformer) 기반 물체 감지 어댑터."""

    def __init__(self, model_id: str = "PekingU/rtdetr_r50vd", device: str = "cpu") -> None:
        self._device = torch.device(device)
        self._processor = RTDetrImageProcessor.from_pretrained(model_id)
        self._model = RTDetrForObjectDetection.from_pretrained(model_id).to(self._device)
        self._model.eval()
        logger.info("RT-DETR 물체 감지 모델 로드 완료: %s (device=%s)", model_id, device)

    @torch.no_grad()
    def detect(self, image_bytes: bytes, score_threshold: float) -> ObjectDetectResult:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_format = image.format
            image = image.convert("RGB")
        except UnidentifiedImageError as e:
            raise ValueError("이미지로 인식할 수 없는 파일입니다.") from e

        if image_format not in _SUPPORTED_FORMATS:
            raise ValueError(f"지원하지 않는 이미지 포맷입니다: {image_format}")

        inputs = self._processor(images=image, return_tensors="pt").to(self._device)
        outputs = self._model(**inputs)
        results = self._processor.post_process_object_detection(
            outputs, target_sizes=torch.tensor([image.size[::-1]]), threshold=score_threshold
        )[0]

        id2label = self._model.config.id2label
        objects = [
            DetectedObject(
                label=id2label[int(label_id)],
                confidence=round(float(score), 4),
                # post_process_object_detection은 xyxy(절대 픽셀)를 반환한다 — 스펙 문서의
                # 출력 계약(x, y, w, h)에 맞춰 xywh로 변환한다.
                box=BoundingBox(
                    x=round(float(box[0]), 2),
                    y=round(float(box[1]), 2),
                    w=round(float(box[2] - box[0]), 2),
                    h=round(float(box[3] - box[1]), 2),
                ),
            )
            for score, label_id, box in zip(
                results["scores"], results["labels"], results["boxes"]
            )
        ]
        return ObjectDetectResult(objects=objects, instance_count=len(objects))
