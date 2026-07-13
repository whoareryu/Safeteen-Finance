from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.care_prescription_entity import CarePrescriptionEntity


class CarePrescriptionRepository(ABC):

    @abstractmethod
    async def save(self, entity: CarePrescriptionEntity) -> CarePrescriptionEntity:
        pass

    @abstractmethod
    async def find_by_diagnosis(self, diagnosis_record_id: int) -> CarePrescriptionEntity | None:
        pass
