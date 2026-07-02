"""JminJ/kcElectra_base_Bad_Sentence_Classifier 기반 한국어 욕설·혐오 표현 탐지.

transformers 미설치 환경에서는 키워드 매칭으로 자동 폴백한다.
"""
from __future__ import annotations

import logging

from chef.app.ports.output.guardrail_port import GuardrailPort, GuardrailVerdict

logger = logging.getLogger(__name__)

_MODEL_NAME = "JminJ/kcElectra_base_Bad_Sentence_Classifier"
_VIOLATION_THRESHOLD = 0.50

# transformers 미설치 환경 폴백용 키워드 어휘집
_FALLBACK_LEXICON: dict[str, list[str]] = {
    "악플/욕설": [
        "그딴", "때려쳐", "때려쳐라", "ㅉㅉ", "씨발", "시발", "씨x", "ㅅㅂ",
        "개새끼", "개새x", "꺼져", "닥쳐", "병신", "빙신", "멍청", "쓰레기",
        "찐따", "돌아이", "미친", "엿먹", "지랄", "개xx", "빡대가리",
    ],
    "혐오/모욕": [
        "이딴", "한심", "뭐하는", "저능", "무뇌", "열폭",
    ],
    "기타 혐오": [
        "죽어", "꺼지라", "없어져",
    ],
}


class KcElectraUnsmileClassifier(GuardrailPort):
    """JminJ/kcElectra_base_Bad_Sentence_Classifier v2 분류기.

    모델 로드 실패 시 키워드 매칭으로 자동 폴백.
    """

    def __init__(self) -> None:
        self._tokenizer = None
        self._model = None
        self._torch = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
            self._model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
            self._model.eval()
            self._torch = torch
            logger.info("[KcELECTRA] 분류 모델 로드 완료 (%s)", _MODEL_NAME)
        except Exception as exc:
            logger.warning("[KcELECTRA] 모델 로드 실패 → 키워드 매칭으로 전환: %s", exc)

    def score(self, text: str) -> GuardrailVerdict:
        if self._model is not None:
            return self._score_with_model(text)
        return self._score_with_lexicon(text)

    def _score_with_model(self, text: str) -> GuardrailVerdict:
        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512, padding=True,
        )
        with self._torch.no_grad():
            logits = self._model(**inputs).logits
            probs = self._torch.softmax(logits, dim=-1)
        bad_score = round(probs[0][0].item(), 3)  # label 0 = "Bad sentence"
        return GuardrailVerdict(
            violates=bad_score >= _VIOLATION_THRESHOLD,
            score=bad_score,
        )

    def _score_with_lexicon(self, text: str) -> GuardrailVerdict:
        matched_by_category: dict[str, list[str]] = {}
        for category, keywords in _FALLBACK_LEXICON.items():
            hits = [kw for kw in keywords if kw in text]
            if hits:
                matched_by_category[category] = hits

        all_matched = [kw for hits in matched_by_category.values() for kw in hits]
        hit_count = len(all_matched)
        raw_score = (0.55 + 0.15 * (hit_count - 1)) if hit_count > 0 else 0.03
        violation_score = round(min(raw_score, 1.0), 3)

        return GuardrailVerdict(
            violates=violation_score >= _VIOLATION_THRESHOLD,
            score=violation_score,
            matched=all_matched,
            categories=list(matched_by_category.keys()),
        )


_singleton: KcElectraUnsmileClassifier | None = None


def get_kc_electra_guardrail() -> KcElectraUnsmileClassifier:
    global _singleton
    if _singleton is None:
        _singleton = KcElectraUnsmileClassifier()
    return _singleton
