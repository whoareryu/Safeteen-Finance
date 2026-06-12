from __future__ import annotations

from typing import Any

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterRoasterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.output.crew_walter_roaster_repository import WalterRoasterRepository


class WalterRoasterInteractor(WalterRoasterUseCase):
    
    def __init__(self, repository: WalterRoasterRepository):
        self.repository = repository

    async def introduce_myself(self, schema: WalterRoasterSchema) -> WalterRoasterResponse:
        '''왈터 로스터의 자기소개 인터렉트'''
        query = WalterRoasterQuery(
            id = schema.id,
            name = schema.name
        )
        return await self.repository.introduce_myself(WalterRoasterQuery(
            id = schema.id,
            name = schema.name
        ))
        