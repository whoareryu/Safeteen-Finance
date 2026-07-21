from __future__ import annotations

from ontology.app.dtos.sentiment_analysis_dto import SentimentAnalyzeCommand, SentimentAnalyzeResult
from ontology.app.ports.input.sentiment_analysis_use_case import SentimentAnalysisUseCase
from ontology.app.ports.output.sentiment_analysis_model_port import SentimentAnalysisModelPort


class SentimentAnalysisInteractor(SentimentAnalysisUseCase):
    """ontology 허브의 감정 분석 캐퍼빌리티 — KLUE/KoELECTRA 등 분류 백엔드를 감싼다."""

    def __init__(self, model: SentimentAnalysisModelPort) -> None:
        self._model = model

    def analyze(self, command: SentimentAnalyzeCommand) -> SentimentAnalyzeResult:
        return self._model.analyze(command.text)
