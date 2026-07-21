from __future__ import annotations

import logging

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ontology.app.dtos.sentiment_analysis_dto import SentimentAnalyzeResult, SentimentScore
from ontology.app.ports.output.sentiment_analysis_model_port import SentimentAnalysisModelPort

logger = logging.getLogger(__name__)

_MAX_TOKEN_LENGTH = 256


class SentimentClassifierModelAdapter(SentimentAnalysisModelPort):
    """분류 헤드가 이미 파인튜닝된 한국어 감정분석 체크포인트를 로드해 추론하는 어댑터.

    문서(sentiment-analysis.md)가 추천하는 klue/roberta-large는 QLoRA 파인튜닝 전에는
    분류 헤드가 랜덤 초기화 상태라 그대로 쓰면 안 된다. 기본값으로 NSMC에 이미
    파인튜닝된 monologg/koelectra-base-finetuned-nsmc를 쓰고, 다른 파인튜닝 체크포인트로
    교체 가능하도록 model_id를 그대로 노출한다.
    """

    def __init__(
        self, model_id: str = "monologg/koelectra-base-finetuned-nsmc", device: str = "cpu"
    ) -> None:
        self._device = torch.device(device)
        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_id).to(self._device)
        self._model.eval()
        self._id2label: dict[int, str] = self._model.config.id2label
        logger.info(
            "감정 분석 모델 로드 완료: %s (클래스 %d개, device=%s)",
            model_id, len(self._id2label), device,
        )

    @torch.no_grad()
    def analyze(self, text: str) -> SentimentAnalyzeResult:
        if not text.strip():
            raise ValueError("빈 텍스트는 감정 분석할 수 없습니다.")

        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=_MAX_TOKEN_LENGTH
        ).to(self._device)
        outputs = self._model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        top_id = int(torch.argmax(probs))

        scores = [
            SentimentScore(label=self._id2label[i], score=round(float(prob), 4))
            for i, prob in enumerate(probs)
        ]
        return SentimentAnalyzeResult(
            sentiment=self._id2label[top_id],
            confidence=round(float(probs[top_id]), 4),
            scores=scores,
        )
