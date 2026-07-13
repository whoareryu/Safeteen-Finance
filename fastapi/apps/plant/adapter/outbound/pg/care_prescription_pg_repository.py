from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.care_prescription_orm import CarePrescriptionORM
from plant.adapter.outbound.orm_mappers.care_prescription_orm_mapper import to_entity, to_orm
from plant.app.ports.output.care_prescription_repository import CarePrescriptionRepository
from plant.domain.entities.care_prescription_entity import CarePrescriptionEntity


class CarePrescriptionPgRepository(CarePrescriptionRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: CarePrescriptionEntity) -> CarePrescriptionEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def find_by_diagnosis(self, diagnosis_record_id: int) -> CarePrescriptionEntity | None:
        query = select(CarePrescriptionORM).where(
            CarePrescriptionORM.diagnosis_record_id == diagnosis_record_id
        )
        result = await self.session.execute(query)
        orm = result.scalar_one_or_none()
        return to_entity(orm) if orm is not None else None
