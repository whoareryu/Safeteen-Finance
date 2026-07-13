from __future__ import annotations

import asyncio

from ontology.app.dtos.yolo_dto import YoloPredictCommand
from ontology.app.ports.input.yolo_use_case import YoloUseCase
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from plant.app.dtos.diagnosis_dto import DiagnosisResult, DiagnosisUploadCommand
from plant.app.ports.input.diagnosis_use_case import DiagnosisUseCase
from plant.app.ports.output.diagnosis_repository import DiagnosisRepository
from plant.app.ports.output.plant_repository import PlantRepository
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity

_UNKNOWN_LABEL = "unknown__unknown"


def _parse_label(label: str) -> tuple[str, str]:
    """YOLO 분류 라벨 `{species}__{symptom}`을 (species, symptom)으로 분리한다."""
    if "__" not in label:
        return label, "healthy"
    species, symptom = label.split("__", 1)
    return species, symptom


class DiagnosisInteractor(DiagnosisUseCase):

    def __init__(
        self,
        plant_repository: PlantRepository,
        diagnosis_repository: DiagnosisRepository,
        yolo: YoloUseCase,
        storage: ImageStorageGateway,
    ) -> None:
        self._plant_repository = plant_repository
        self._diagnosis_repository = diagnosis_repository
        self._yolo = yolo
        self._storage = storage

    async def diagnose(self, command: DiagnosisUploadCommand) -> DiagnosisResult:
        photo_url = await self._storage.save(command.filename, command.content_type, command.data)

        prediction = await asyncio.to_thread(
            self._yolo.predict, YoloPredictCommand(image=command.data)
        )
        species, symptom = _parse_label(prediction.name or _UNKNOWN_LABEL)

        plant = await self._plant_repository.find_or_create(
            owner_user_id=command.owner_user_id,
            region=command.region,
            species_hint=species,
        )

        record = await self._diagnosis_repository.save(
            DiagnosisRecordEntity(
                id=None,
                plant_id=plant.id,  # type: ignore[arg-type]
                photo_url=photo_url,
                detected_species=species,
                species_confidence=prediction.confidence,
                symptom_label=symptom,
                symptom_confidence=prediction.confidence,
            )
        )
        return self._to_result(record)

    async def get(self, diagnosis_id: int) -> DiagnosisResult:
        record = await self._diagnosis_repository.get(diagnosis_id)
        return self._to_result(record)

    @staticmethod
    def _to_result(record: DiagnosisRecordEntity) -> DiagnosisResult:
        return DiagnosisResult(
            id=record.id,  # type: ignore[arg-type]
            plant_id=record.plant_id,
            photo_url=record.photo_url,
            detected_species=record.detected_species,
            species_confidence=record.species_confidence,
            symptom_label=record.symptom_label,
            symptom_confidence=record.symptom_confidence,
        )
