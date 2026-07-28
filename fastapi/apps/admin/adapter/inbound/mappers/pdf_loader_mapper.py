from __future__ import annotations

from admin.adapter.inbound.api.schemas.pdf_loader_schema import PdfSummaryResponse
from admin.app.dtos.pdf_loader_dto import PdfSummaryResult


def to_response(result: PdfSummaryResult) -> PdfSummaryResponse:
    return PdfSummaryResponse(
        id=result.id,
        filename=result.filename,
        extracted_text=result.extracted_text,
        summary=result.summary,
    )
