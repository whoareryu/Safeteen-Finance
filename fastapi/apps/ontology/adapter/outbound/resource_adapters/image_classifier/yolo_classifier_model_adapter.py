from __future__ import annotations

import io

from PIL import Image
from ultralytics import YOLO

from ontology.app.dtos.image_classifier_dto import ImageClassifyResult
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.ports.output.yolo_model_port import YoloModelPort


class YoloClassifierModelAdapter(ImageClassifierModelPort):
    """YOLO(ultralytics) 분류 가중치 — 통합 이미지 분류 포트의 한 backend.

    YOLO는 자체 전처리를 내부에서 처리하므로(ConvNeXt의 ImageNet 정규화와 다름),
    여기서 별도 preprocess_bytes를 적용하지 않는다.
    """

    def __init__(self, model_port: YoloModelPort, device: str = "cpu") -> None:
        self._model_port = model_port
        self._device = device

    def predict(self, image_bytes: bytes) -> ImageClassifyResult:
        weights_path = self._model_port.load_path()
        model = YOLO(weights_path)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        results = model.predict(source=image, device=self._device, verbose=False)
        probs = results[0].probs
        top1 = int(probs.top1)
        return ImageClassifyResult(
            label=results[0].names[top1], confidence=round(float(probs.top1conf), 4)
        )
