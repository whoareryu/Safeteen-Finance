from __future__ import annotations

from pydantic import BaseModel


class DiagnosisUploadResponse(BaseModel):
    id: int
    plant_id: int
    photo_url: str
    detected_species: str
    species_confidence: float
    symptom_label: str
    symptom_confidence: float


class DiagnosisDetailResponse(DiagnosisUploadResponse):
    pass
