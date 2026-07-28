from __future__ import annotations

from pydantic import BaseModel


class PdfSummaryResponse(BaseModel):
    id: int
    filename: str
    extracted_text: str
    summary: str
