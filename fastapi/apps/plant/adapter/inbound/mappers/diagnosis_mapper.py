from __future__ import annotations

from plant.adapter.inbound.api.schemas.diagnosis_schema import (
    DiagnosisDetailResponse,
    DiagnosisUploadResponse,
)
from plant.app.dtos.diagnosis_dto import DiagnosisResult


def to_upload_response(result: DiagnosisResult) -> DiagnosisUploadResponse:
    return DiagnosisUploadResponse(
        id=result.id,
        plant_id=result.plant_id,
        photo_url=result.photo_url,
        detected_species=result.detected_species,
        species_confidence=result.species_confidence,
        symptom_label=result.symptom_label,
        symptom_confidence=result.symptom_confidence,
    )


def to_detail_response(result: DiagnosisResult) -> DiagnosisDetailResponse:
    return DiagnosisDetailResponse(**to_upload_response(result).model_dump())
