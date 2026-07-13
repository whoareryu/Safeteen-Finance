from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CarePrescriptionEntity:
    id: int | None
    diagnosis_record_id: int
    prescription_text: str
    llm_model: str
    generated_at: datetime | None = None
