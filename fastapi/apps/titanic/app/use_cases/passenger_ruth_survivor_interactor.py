from __future__ import annotations

from titanic.adapter.inbound.api.schemas.passenger_ruth_survivor_schema import RuthSurvivorSchema
from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorQuery, RuthSurvivorResponse
from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthSurvivorUseCase
from titanic.app.ports.output.passenger_ruth_survivor_port import RuthSurvivorPort


class RuthSurvivorInteractor(RuthSurvivorUseCase):

    def __init__(self, repository: RuthSurvivorPort):
        self.repository = repository

    async def introduce_myself(self, schema) -> RuthSurvivorResponse:
        schema = RuthSurvivorSchema(id=14, name="루스 드윗 부카터 (Ruth DeWitt Bukater)")
        return RuthSurvivorResponse(id=schema.id, name=schema.name)
        
        