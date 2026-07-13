from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosisUploadCommand:
    owner_user_id: int | None
    region: str
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class DiagnosisResult:
    id: int
    plant_id: int
    photo_url: str
    detected_species: str
    species_confidence: float
    symptom_label: str
    symptom_confidence: float
