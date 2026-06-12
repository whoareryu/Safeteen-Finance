from __future__ import annotations

from typing import Any

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository


class HartleyViolinInteractor(HartleyViolinUseCase):
    
    def __init__(self, repository: HartleyViolinRepository):
        self.repository = repository

    async def introduce_myself(self, schema: HartleyViolinSchema) -> HartleyViolinResponse:
        '''하트리 위올린의 자기소개 인터렉트'''
        query = HartleyViolinQuery(
            id = schema.id,
            name = schema.name
        )
        return await self.repository.introduce_myself(HartleyViolinQuery(
            id = schema.id,
            name = schema.name
        ))
        