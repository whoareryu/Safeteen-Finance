from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.output.passenger_cal_tester_repository import CalTesterRepository

logger = logging.getLogger(__name__)


class CalTesterPGRepository(CalTesterRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: CalTesterQuery) -> CalTesterResponse:
        return CalTesterResponse(id=query.id * 10000, name=query.name)
