from __future__ import annotations

from ontology.app.dtos.sentiment_analysis_dto import (
    SentimentAnalyzeCommand,
    SentimentAnalyzeResult,
    SentimentScore,
)
from ontology.app.ports.output.sentiment_analysis_model_port import SentimentAnalysisModelPort
from ontology.app.use_cases.sentiment_analysis_interactor import SentimentAnalysisInteractor


class _FakeModelPort(SentimentAnalysisModelPort):
    def __init__(self, result: SentimentAnalyzeResult) -> None:
        self._result = result
        self.received_text: str | None = None

    def analyze(self, text: str) -> SentimentAnalyzeResult:
        self.received_text = text
        return self._result


def test_analyze_delegates_to_model_port() -> None:
    expected = SentimentAnalyzeResult(
        sentiment="positive",
        confidence=0.93,
        scores=[SentimentScore(label="negative", score=0.07), SentimentScore(label="positive", score=0.93)],
    )
    model = _FakeModelPort(expected)
    interactor = SentimentAnalysisInteractor(model=model)

    result = interactor.analyze(SentimentAnalyzeCommand(text="이 영화 진짜 재밌다"))

    assert result is expected
    assert model.received_text == "이 영화 진짜 재밌다"
