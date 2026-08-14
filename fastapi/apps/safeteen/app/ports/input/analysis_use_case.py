from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.analysis_dto import AnalysisResult, AnalyzeCommand


class AnalysisUseCase(ABC):
    """Inbound 입력 포트 — SNS 불법 금융 광고 텍스트/이미지 위험도 분석."""

    @abstractmethod
    async def analyze(self, command: AnalyzeCommand) -> AnalysisResult:
        pass
