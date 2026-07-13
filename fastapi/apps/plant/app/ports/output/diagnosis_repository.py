from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity


class DiagnosisRepository(ABC):

    @abstractmethod
    async def save(self, entity: DiagnosisRecordEntity) -> DiagnosisRecordEntity:
        pass

    @abstractmethod
    async def get(self, diagnosis_id: int) -> DiagnosisRecordEntity:
        pass
