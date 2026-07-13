from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.diagnosis_record_orm import DiagnosisRecordORM
from plant.adapter.outbound.orm_mappers.diagnosis_orm_mapper import to_entity, to_orm
from plant.app.ports.output.diagnosis_repository import DiagnosisRepository
from plant.domain.entities.diagnosis_record_entity import DiagnosisRecordEntity


class DiagnosisPgRepository(DiagnosisRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: DiagnosisRecordEntity) -> DiagnosisRecordEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def get(self, diagnosis_id: int) -> DiagnosisRecordEntity:
        orm = await self.session.get(DiagnosisRecordORM, diagnosis_id)
        if orm is None:
            raise ValueError(f"Diagnosis record {diagnosis_id} not found")
        return to_entity(orm)
