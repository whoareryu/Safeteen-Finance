from __future__ import annotations

from typing import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from plant.adapter.outbound.pg.diagnosis_pg_repository import DiagnosisPgRepository
from plant.adapter.outbound.pg.plant_pg_repository import PlantPgRepository
from plant.app.ports.input.diagnosis_use_case import DiagnosisUseCase
from plant.app.use_cases.diagnosis_interactor import DiagnosisInteractor

# composition root(main.py)에서 등록하는 팩토리 — ontology 허브의 어댑터를 plant 전용 설정으로 주입한다.
_species_classifier_factory: Callable[[], ImageClassifierModelPort] | None = None
_image_storage_factory: Callable[[], ImageStorageGateway] | None = None


def register_species_classifier_factory(factory: Callable[[], ImageClassifierModelPort]) -> None:
    global _species_classifier_factory
    _species_classifier_factory = factory


def register_image_storage_factory(factory: Callable[[], ImageStorageGateway]) -> None:
    global _image_storage_factory
    _image_storage_factory = factory


def _get_species_classifier() -> ImageClassifierModelPort:
    if _species_classifier_factory is None:
        raise RuntimeError("species classifier factory가 등록되지 않았습니다 (main.py composition root 확인)")
    return _species_classifier_factory()


def _get_image_storage_gateway() -> ImageStorageGateway:
    if _image_storage_factory is None:
        raise RuntimeError("image storage factory가 등록되지 않았습니다 (main.py composition root 확인)")
    return _image_storage_factory()


def get_diagnosis_use_case(db: AsyncSession = Depends(get_db)) -> DiagnosisUseCase:
    return DiagnosisInteractor(
        plant_repository=PlantPgRepository(session=db),
        diagnosis_repository=DiagnosisPgRepository(session=db),
        species_classifier=_get_species_classifier(),
        storage=_get_image_storage_gateway(),
    )
