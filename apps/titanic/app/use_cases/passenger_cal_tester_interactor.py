from __future__ import annotations

from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.output.passenger_cal_tester_repository import CalTesterRepository


class CalTesterInteractor(CalTesterUseCase):
    
    def __init__(self, repository: CalTesterRepository):
        self.repository = repository

    async def introduce_myself(self, schema: CalTesterSchema) -> CalTesterResponse:
        '''캘 테스터의 자기소개 인터렉트'''
        query = CalTesterQuery(
            id = schema.id,
            name = schema.name
        )
        return await self.repository.introduce_myself(CalTesterQuery(
            id = schema.id,
            name = schema.name
        ))
        