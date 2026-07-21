from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import cv2
import numpy as np
import torch
from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor

from ontology.app.dtos.video_classification_dto import ClipSegment, LabelScore, VideoClassifyResult
from ontology.app.ports.output.video_classification_model_port import VideoClassificationModelPort

logger = logging.getLogger(__name__)

# 프레임 디코딩은 문서(video-classification.md §3-3)가 권장하는 decord 대신, 이미 프로젝트에
# 고정 의존성으로 있는 opencv-python(cv2)을 재사용해 새 의존성 추가 없이 동일한 균등 샘플링을 구현했다.


class VideoMaeModelAdapter(VideoClassificationModelPort):
    """VideoMAE(ViT 기반 Video Transformer) 동영상 행동 분류 어댑터.

    §3의 전체 클립 분류와 §5의 슬라이딩 윈도우 구간 분류를 모두 수행한다.
    """

    _NUM_FRAMES = 16
    _STRIDE = 8
    _TOP_K = 5
    _SEGMENT_THRESHOLD = 0.5

    def __init__(
        self, model_id: str = "MCG-NJU/videomae-base-finetuned-kinetics", device: str = "cpu"
    ) -> None:
        self._device = torch.device(device)
        self._processor = VideoMAEImageProcessor.from_pretrained(model_id)
        self._model = VideoMAEForVideoClassification.from_pretrained(model_id).to(self._device)
        self._model.eval()
        self._id2label: dict[int, str] = self._model.config.id2label
        logger.info(
            "VideoMAE 동영상 분류 모델 로드 완료: %s (클래스 %d개, device=%s)",
            model_id, len(self._id2label), device,
        )

    def classify(self, video_bytes: bytes, filename: str) -> VideoClassifyResult:
        suffix = Path(filename).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
            tmp.write(video_bytes)
            tmp.flush()

            cap = cv2.VideoCapture(tmp.name)
            if not cap.isOpened():
                cap.release()
                raise ValueError("동영상을 열 수 없습니다. 지원하지 않는 포맷일 수 있습니다.")
            try:
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                if total_frames < 2:
                    raise ValueError("동영상에서 프레임을 읽을 수 없습니다.")

                overall_probs = self._classify_clip(cap, 0, total_frames)
                top_id = int(torch.argmax(overall_probs))
                k = min(self._TOP_K, overall_probs.numel())
                top_k_indices = torch.topk(overall_probs, k).indices
                top_k_labels = [
                    LabelScore(label=self._id2label[int(i)], score=round(float(overall_probs[i]), 4))
                    for i in top_k_indices
                ]

                return VideoClassifyResult(
                    action_label=self._id2label[top_id],
                    confidence=round(float(overall_probs[top_id]), 4),
                    top_k_labels=top_k_labels,
                    clip_segments=self._sliding_window_segments(cap, total_frames, fps),
                )
            finally:
                cap.release()

    @torch.no_grad()
    def _classify_clip(self, cap: cv2.VideoCapture, start: int, end: int) -> torch.Tensor:
        indices = np.linspace(start, end - 1, self._NUM_FRAMES, dtype=int)
        frames = [self._read_frame(cap, int(idx)) for idx in indices]
        inputs = self._processor(frames, return_tensors="pt").to(self._device)
        outputs = self._model(**inputs)
        return torch.softmax(outputs.logits, dim=-1)[0]

    def _read_frame(self, cap: cv2.VideoCapture, frame_index: int) -> np.ndarray:
        cap.set(cv2.CAP_PROP_POS_FRAMES, float(frame_index))
        ok, frame_bgr = cap.read()
        if not ok:
            raise ValueError(f"{frame_index}번 프레임을 읽을 수 없습니다.")
        return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    def _sliding_window_segments(
        self, cap: cv2.VideoCapture, total_frames: int, fps: float
    ) -> list[ClipSegment]:
        if total_frames <= self._NUM_FRAMES:
            return []

        segments: list[ClipSegment] = []
        for start in range(0, total_frames - self._NUM_FRAMES, self._STRIDE):
            end = start + self._NUM_FRAMES
            probs = self._classify_clip(cap, start, end)
            top_id = int(torch.argmax(probs))
            confidence = float(probs[top_id])
            if confidence >= self._SEGMENT_THRESHOLD:
                segments.append(
                    ClipSegment(
                        start_sec=round(start / fps, 2),
                        end_sec=round(end / fps, 2),
                        label=self._id2label[top_id],
                        confidence=round(confidence, 4),
                    )
                )
        return segments
