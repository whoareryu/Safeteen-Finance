from __future__ import annotations

from plant.adapter.outbound.orm.care_prescription_orm import CarePrescriptionORM
from plant.domain.entities.care_prescription_entity import CarePrescriptionEntity


def to_entity(orm: CarePrescriptionORM) -> CarePrescriptionEntity:
    return CarePrescriptionEntity(
        id=orm.id,
        diagnosis_record_id=orm.diagnosis_record_id,
        prescription_text=orm.prescription_text,
        llm_model=orm.llm_model,
        generated_at=orm.generated_at,
    )


def to_orm(entity: CarePrescriptionEntity) -> CarePrescriptionORM:
    return CarePrescriptionORM(
        diagnosis_record_id=entity.diagnosis_record_id,
        prescription_text=entity.prescription_text,
        llm_model=entity.llm_model,
    )
