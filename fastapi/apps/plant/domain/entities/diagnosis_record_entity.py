from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiagnosisRecordEntity:
    id: int | None
    plant_id: int
    photo_url: str
    detected_species: str
    species_confidence: float
    symptom_label: str
    symptom_confidence: float
    diagnosed_at: datetime | None = None
