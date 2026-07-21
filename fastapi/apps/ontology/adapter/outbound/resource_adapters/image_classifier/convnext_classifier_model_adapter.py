from __future__ import annotations

import io
import json
import logging
import os

import timm
import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

from ontology.app.dtos.image_classifier_dto import ImageClassifyResult
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort

logger = logging.getLogger(__name__)

_SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

_TRANSFORM = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def _preprocess_bytes(image_bytes: bytes) -> torch.Tensor:
    """이미지 bytes를 ConvNeXt 입력 (1, 3, 224, 224) 텐서로 변환한다.

    지원 포맷(JPEG/PNG/WEBP)이 아니거나 이미지로 열 수 없으면 ValueError를 raise한다.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image_format = image.format
        image = image.convert("RGB")
    except UnidentifiedImageError as e:
        raise ValueError("이미지로 인식할 수 없는 파일입니다.") from e

    if image_format not in _SUPPORTED_FORMATS:
        raise ValueError(f"지원하지 않는 이미지 포맷입니다: {image_format}")

    tensor = _TRANSFORM(image)
    return tensor.unsqueeze(0)


class ConvNeXtClassifierModelAdapter(ImageClassifierModelPort):
    """ConvNeXt Nano(timm) 파인튜닝 가중치를 로드해 추론하는 어댑터."""

    def __init__(self, weights_path: str, class_names_path: str, device: str = "cpu") -> None:
        if not os.path.exists(weights_path):
            raise RuntimeError(f"분류 모델 가중치를 찾을 수 없습니다: {weights_path}")
        if not os.path.exists(class_names_path):
            raise RuntimeError(f"클래스 이름 파일을 찾을 수 없습니다: {class_names_path}")

        with open(class_names_path, encoding="utf-8") as f:
            self._class_names: list[str] = json.load(f)

        self._device = torch.device(device)
        self._model = timm.create_model(
            "convnext_nano", pretrained=False, num_classes=len(self._class_names)
        )
        state_dict = torch.load(weights_path, map_location=self._device)
        self._model.load_state_dict(state_dict)
        self._model.to(self._device)
        self._model.eval()
        logger.info(
            "ConvNeXt 분류 모델 로드 완료: %s (클래스 %d개, device=%s)",
            weights_path, len(self._class_names), device,
        )

    @torch.no_grad()
    def predict(self, image_bytes: bytes) -> ImageClassifyResult:
        tensor = _preprocess_bytes(image_bytes).to(self._device)
        logits = self._model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        confidence, index = torch.max(probs, dim=0)
        return ImageClassifyResult(
            label=self._class_names[int(index)], confidence=round(float(confidence), 4)
        )
