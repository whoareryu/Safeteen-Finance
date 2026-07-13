from __future__ import annotations

from pydantic import BaseModel


class CareGuideResponse(BaseModel):
    id: int
    diagnosis_record_id: int
    prescription_text: str
