from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.sentiment_analysis_dto import SentimentAnalyzeCommand, SentimentAnalyzeResult


class SentimentAnalysisUseCase(ABC):
    """Inbound 입력 포트 — 한국어 텍스트 감정 분석."""

    @abstractmethod
    def analyze(self, command: SentimentAnalyzeCommand) -> SentimentAnalyzeResult:
        """텍스트의 감정 클래스와 클래스별 확률을 반환한다."""
        pass
