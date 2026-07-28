from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.pdf_loader_dto import PdfSummaryResult, PdfUploadCommand


class PdfLoaderUseCase(ABC):
    """Inbound 입력 포트 — PDF 업로드 기반 텍스트 추출·요약."""

    @abstractmethod
    async def summarize(self, command: PdfUploadCommand) -> PdfSummaryResult:
        pass

    @abstractmethod
    async def get(self, document_id: int) -> PdfSummaryResult:
        pass
