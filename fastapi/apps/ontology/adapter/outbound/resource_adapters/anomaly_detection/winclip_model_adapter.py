from __future__ import annotations

import io
import logging

import torch
from PIL import Image, UnidentifiedImageError
from transformers import CLIPModel, CLIPProcessor

from ontology.app.dtos.anomaly_detection_dto import AnomalyDetectResult, DefectScore
from ontology.app.ports.output.anomaly_detection_model_port import AnomalyDetectionModelPort

logger = logging.getLogger(__name__)

_SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

# anomaly-detection.md §3-3 WinCLIP 프롬프트 세트를 그대로 사용한다.
_NORMAL_PROMPTS = [
    "a photo of a normal product",
    "a photo of a good quality item",
]
_ANOMALY_PROMPT_TEMPLATES = [
    "a photo of a {defect_type} on the surface",
    "a photo of a product with {defect_type}",
    "a defective product showing {defect_type}",
]


class WinClipModelAdapter(AnomalyDetectionModelPort):
    """CLIP + 텍스트 프롬프트 기반 zero-shot 이상 탐지 어댑터(WinCLIP 방식).

    정상 샘플 학습(Memory Bank 구축) 없이 사전학습된 CLIP만으로 바로 동작한다 —
    PatchCore/FastFlow와 달리 도메인별 정상 이미지 데이터셋이 필요 없다.
    """

    def __init__(self, model_id: str = "openai/clip-vit-base-patch32", device: str = "cpu") -> None:
        self._device = torch.device(device)
        self._processor = CLIPProcessor.from_pretrained(model_id)
        self._model = CLIPModel.from_pretrained(model_id).to(self._device)
        self._model.eval()
        logger.info("WinCLIP 이상 탐지 모델 로드 완료: %s (device=%s)", model_id, device)

    @torch.no_grad()
    def detect(
        self, image_bytes: bytes, defect_types: list[str], threshold: float
    ) -> AnomalyDetectResult:
        if not defect_types:
            raise ValueError("defect_types가 비어 있습니다.")

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_format = image.format
            image = image.convert("RGB")
        except UnidentifiedImageError as e:
            raise ValueError("이미지로 인식할 수 없는 파일입니다.") from e

        if image_format not in _SUPPORTED_FORMATS:
            raise ValueError(f"지원하지 않는 이미지 포맷입니다: {image_format}")

        prompts = list(_NORMAL_PROMPTS)
        defect_ranges: dict[str, tuple[int, int]] = {}
        for defect_type in defect_types:
            start = len(prompts)
            prompts.extend(template.format(defect_type=defect_type) for template in _ANOMALY_PROMPT_TEMPLATES)
            defect_ranges[defect_type] = (start, len(prompts))

        inputs = self._processor(
            text=prompts, images=image, return_tensors="pt", padding=True
        ).to(self._device)
        outputs = self._model(**inputs)
        logits = outputs.logits_per_image[0]

        normal_mean = logits[: len(_NORMAL_PROMPTS)].mean()

        # 원본 로짓 차이는 스케일이 커서(logit_scale) 그대로 쓰면 §4 출력 계약(0~1)을
        # 못 지킨다. sigmoid로 정규화하면 0.5가 "정상/이상 경계"가 되어 문서의
        # "양수 → 이상" 판정과 그대로 대응된다.
        defect_scores = [
            DefectScore(
                defect_type=defect_type,
                score=round(float(torch.sigmoid(logits[start:end].mean() - normal_mean)), 4),
            )
            for defect_type, (start, end) in defect_ranges.items()
        ]

        top = max(defect_scores, key=lambda d: d.score)
        is_anomaly = top.score > threshold
        return AnomalyDetectResult(
            is_anomaly=is_anomaly,
            anomaly_score=top.score,
            defect_category=top.defect_type if is_anomaly else "normal",
            defect_scores=defect_scores,
        )
