from __future__ import annotations

from plant.adapter.outbound.orm.diagnosis_record_orm import DiagnosisRecordORM
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity


def to_entity(orm: DiagnosisRecordORM) -> DiagnosisRecordEntity:
    return DiagnosisRecordEntity(
        id=orm.id,
        plant_id=orm.plant_id,
        photo_url=orm.photo_url,
        detected_species=orm.detected_species,
        species_confidence=orm.species_confidence,
        symptom_label=orm.symptom_label,
        symptom_confidence=orm.symptom_confidence,
        diagnosed_at=orm.diagnosed_at,
    )


def to_orm(entity: DiagnosisRecordEntity) -> DiagnosisRecordORM:
    return DiagnosisRecordORM(
        plant_id=entity.plant_id,
        photo_url=entity.photo_url,
        detected_species=entity.detected_species,
        species_confidence=entity.species_confidence,
        symptom_label=entity.symptom_label,
        symptom_confidence=entity.symptom_confidence,
    )
