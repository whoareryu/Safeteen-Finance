from __future__ import annotations

import asyncio

from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from plant.app.dtos.diagnosis_dto import DiagnosisResult, DiagnosisUploadCommand
from plant.app.ports.input.diagnosis_use_case import DiagnosisUseCase
from plant.app.ports.output.diagnosis_repository import DiagnosisRepository
from plant.app.ports.output.plant_repository import PlantRepository
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity
from plant.domain.value_objects.plant_label_translator import SYMPTOM_NOT_ASSESSED

_UNKNOWN_LABEL = "unknown__unknown"


def _parse_label(label: str) -> tuple[str, str]:
    """YOLO 분류 라벨을 (species, symptom)으로 분리한다.

    `{species}__{symptom}` 결합 라벨(기존 농작물 병해 모델)이면 그대로 분리하고,
    `__`가 없는 품종 전용 라벨(하우스플랜트 모델)이면 증상은 "미판정"으로 둔다 —
    "healthy"로 임의 대체하면 실제로는 모르는 상태를 확신하는 것처럼 보이기 때문.
    """
    if "__" not in label:
        return label, SYMPTOM_NOT_ASSESSED
    species, symptom = label.split("__", 1)
    return species, symptom


class DiagnosisInteractor(DiagnosisUseCase):

    def __init__(
        self,
        plant_repository: PlantRepository,
        diagnosis_repository: DiagnosisRepository,
        species_classifier: ImageClassifierModelPort,
        storage: ImageStorageGateway,
    ) -> None:
        self._plant_repository = plant_repository
        self._diagnosis_repository = diagnosis_repository
        self._species_classifier = species_classifier
        self._storage = storage

    async def diagnose(self, command: DiagnosisUploadCommand) -> DiagnosisResult:
        photo_url = await self._storage.save(command.filename, command.content_type, command.data)

        prediction = await asyncio.to_thread(self._species_classifier.predict, command.data)
        species, symptom = _parse_label(prediction.label or _UNKNOWN_LABEL)
        symptom_confidence = 0.0 if symptom == SYMPTOM_NOT_ASSESSED else prediction.confidence

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
                symptom_confidence=symptom_confidence,
            )
        )
        return await self._to_result(record)

    async def get(self, diagnosis_id: int) -> DiagnosisResult:
        record = await self._diagnosis_repository.get(diagnosis_id)
        return await self._to_result(record)

    async def _to_result(self, record: DiagnosisRecordEntity) -> DiagnosisResult:
        # DB에는 storage.save()가 준 원래 URL을 저장해 두고, 응답을 내려줄 때마다
        # 매번 새로 서명한(퍼블릭 접근 불가 버킷에서도 열리는) URL로 바꿔서 돌려준다.
        viewable_url = await self._storage.presigned_url(record.photo_url)
        return DiagnosisResult(
            id=record.id,  # type: ignore[arg-type]
            plant_id=record.plant_id,
            photo_url=viewable_url,
            detected_species=record.detected_species,
            species_confidence=record.species_confidence,
            symptom_label=record.symptom_label,
            symptom_confidence=record.symptom_confidence,
        )
