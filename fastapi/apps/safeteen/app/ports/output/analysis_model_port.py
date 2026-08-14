from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.analysis_dto import AnalysisResult


class AnalysisModelPort(ABC):
    """Outbound 출력 포트 — LLM으로 텍스트/이미지에서 불법 금융 위험 정보를 추출한다."""

    @abstractmethod
    async def analyze(
        self, text: str | None, image_bytes: bytes | None, image_content_type: str | None
    ) -> AnalysisResult:
        pass
