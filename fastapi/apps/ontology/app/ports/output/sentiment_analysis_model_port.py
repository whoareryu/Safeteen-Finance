from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.sentiment_analysis_dto import SentimentAnalyzeResult


class SentimentAnalysisModelPort(ABC):

    @abstractmethod
    def analyze(self, text: str) -> SentimentAnalyzeResult:
        """텍스트를 감정 분류 모델에 통과시켜 결과를 반환한다."""
        pass
