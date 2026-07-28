from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PdfUploadCommand:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class PdfSummaryResult:
    id: int
    filename: str
    extracted_text: str
    summary: str
