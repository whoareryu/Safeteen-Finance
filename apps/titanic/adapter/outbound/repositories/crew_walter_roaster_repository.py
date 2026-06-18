from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerORM
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse
from titanic.app.ports.output.crew_walter_roaster_port import WalterRoasterPort

logger = logging.getLogger(__name__)


class WalterRoasterRepository(WalterRoasterPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_train_set(self) -> pd.DataFrame:
        '''Survived 컬럼이 있는 데이터 전체를 데이터프레임으로 반환하는 메소드'''
        result = await self.session.execute(
            select(JackTrainerORM).where(
                JackTrainerORM.survived.isnot(None),
                JackTrainerORM.survived != "",
            )
        )
        rows = result.scalars().all()
        return pd.DataFrame([
            {
                "passenger_id": r.passenger_id,
                "name": r.name,
                "gender": r.gender,
                "age": r.age,
                "sib_sp": r.sib_sp,
                "parch": r.parch,
                "survived": r.survived,
            }
            for r in rows
        ])

    async def get_test_set(self) -> pd.DataFrame:
        '''Survived 컬럼이 없는 데이터 전체를 데이터프레임으로 반환하는 메소드'''
        result = await self.session.execute(
            select(JackTrainerORM).where(
                or_(
                    JackTrainerORM.survived.is_(None),
                    JackTrainerORM.survived == "",
                )
            )
        )
        rows = result.scalars().all()
        return pd.DataFrame([
            {
                "passenger_id": r.passenger_id,
                "name": r.name,
                "gender": r.gender,
                "age": r.age,
                "sib_sp": r.sib_sp,
                "parch": r.parch,
                "survived": r.survived,
            }
            for r in rows
        ])
        
    
    async def introduce_myself(self, schema: WalterRoasterQuery) -> WalterRoasterResponse:
        logger.info(f"[WalterRoasterRepository] introduce_myself 진입 | request_data={schema}")
        response: WalterRoasterResponse = WalterRoasterResponse(
            id=schema.id * 10000,
            name=schema.name + "가 레포지토리에 다녀옴"
        )
        return response
    