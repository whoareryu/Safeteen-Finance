from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PdfDocumentEntity:
    id: int | None
    filename: str
    extracted_text: str
    summary: str
    created_at: datetime | None = None
