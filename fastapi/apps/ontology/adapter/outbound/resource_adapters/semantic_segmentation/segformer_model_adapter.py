from __future__ import annotations

import colorsys
import io
import logging

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError
from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor

from ontology.app.dtos.semantic_segmentation_dto import ClassArea, SegmentModelOutput
from ontology.app.ports.output.semantic_segmentation_model_port import (
    SemanticSegmentationModelPort,
)

logger = logging.getLogger(__name__)

_SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}
_OVERLAY_ALPHA = 0.5


def _build_palette(num_classes: int) -> list[tuple[int, int, int]]:
    """클래스 수만큼 시각적으로 구분되는 색을 결정론적으로 생성한다(황금비 색상환 회전).

    palette가 spec 문서에 정의돼 있지 않아, 클래스 ID → 고유 색 매핑에 흔히 쓰이는
    표준 기법을 사용했다.
    """
    palette: list[tuple[int, int, int]] = []
    golden_ratio = 0.618033988749895
    hue = 0.0
    for _ in range(num_classes):
        hue = (hue + golden_ratio) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.95)
        palette.append((int(r * 255), int(g * 255), int(b * 255)))
    return palette


class SegformerModelAdapter(SemanticSegmentationModelPort):
    """SegFormer-B2(ADE20K) 기반 시멘틱 분할 어댑터."""

    def __init__(
        self, model_id: str = "nvidia/segformer-b2-finetuned-ade-512-512", device: str = "cpu"
    ) -> None:
        self._device = torch.device(device)
        self._processor = SegformerImageProcessor.from_pretrained(model_id)
        self._model = SegformerForSemanticSegmentation.from_pretrained(model_id).to(self._device)
        self._model.eval()
        self._id2label: dict[int, str] = self._model.config.id2label
        self._palette = _build_palette(len(self._id2label))
        logger.info(
            "SegFormer 분할 모델 로드 완료: %s (클래스 %d개, device=%s)",
            model_id, len(self._id2label), device,
        )

    @torch.no_grad()
    def segment(self, image_bytes: bytes) -> SegmentModelOutput:
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
        # 모델 출력은 다운샘플된 해상도라 원본 크기로 업샘플링한다(3-4절 mIoU 평가 코드와 동일 방식).
        upsampled = F.interpolate(
            outputs.logits, size=image.size[::-1], mode="bilinear", align_corners=False
        )
        mask = upsampled.argmax(dim=1)[0].cpu().numpy()

        return SegmentModelOutput(
            class_areas=self._compute_class_areas(mask),
            overlay_png=self._render_overlay(image, mask),
        )

    def _compute_class_areas(self, mask: np.ndarray) -> list[ClassArea]:
        total_pixels = mask.size
        class_ids, counts = np.unique(mask, return_counts=True)
        areas = [
            ClassArea(
                label=self._id2label.get(int(class_id), str(int(class_id))),
                ratio=round(float(count) / total_pixels, 4),
            )
            for class_id, count in zip(class_ids, counts)
        ]
        areas.sort(key=lambda area: area.ratio, reverse=True)
        return areas

    def _render_overlay(self, image: Image.Image, mask: np.ndarray) -> bytes:
        colored_mask = np.zeros((*mask.shape, 3), dtype=np.uint8)
        for class_id in np.unique(mask):
            colored_mask[mask == class_id] = self._palette[int(class_id) % len(self._palette)]

        overlay = (
            np.array(image) * (1 - _OVERLAY_ALPHA) + colored_mask * _OVERLAY_ALPHA
        ).astype(np.uint8)

        buf = io.BytesIO()
        Image.fromarray(overlay).save(buf, format="PNG")
        return buf.getvalue()
