from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerORM
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerPassengerData, JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository

logger = logging.getLogger(__name__)


class JackTrainerPGRepository(JackTrainerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: JackTrainerQuery) -> JackTrainerResponse:
        return JackTrainerResponse(id=query.id * 10000, name=query.name)

    async def get_training_data(self) -> list[JackTrainerPassengerData]:
        result = await self.session.execute(select(JackTrainerORM))
        rows = result.scalars().all()
        data: list[JackTrainerPassengerData] = []
        for row in rows:
            try:
                survived = int(row.survived)
                age = float(row.age) if row.age not in (None, "", "nan") else 0.0
                sib_sp = int(row.sib_sp) if row.sib_sp not in (None, "") else 0
                parch = int(row.parch) if row.parch not in (None, "") else 0
                gender_raw = (row.gender or "").lower()
                gender = 1 if gender_raw in ("female", "f", "1") else 0
                data.append(JackTrainerPassengerData(
                    survived=survived,
                    age=age,
                    sib_sp=sib_sp,
                    parch=parch,
                    gender=gender,
                ))
            except (ValueError, TypeError):
                continue
        return data
