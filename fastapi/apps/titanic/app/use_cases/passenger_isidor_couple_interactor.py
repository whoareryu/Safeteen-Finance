from __future__ import annotations

from titanic.adapter.inbound.api.schemas.passenger_isidor_couple_schema import IsidorCoupleSchema
from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery, IsidorCoupleResponse
from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorCoupleUseCase
from titanic.app.ports.output.passenger_isidor_couple_port import IsidorCouplePort


class IsidorCoupleInteractor(IsidorCoupleUseCase):

    def __init__(self, repository: IsidorCouplePort):
        self.repository = repository

    async def introduce_myself(self, schema) -> IsidorCoupleResponse:
        schema = IsidorCoupleSchema(id=12, name="이시도르 & 이다 스트라우스 부부 (Isidor & Ida Straus)")
        return IsidorCoupleResponse(id=schema.id, name=schema.name)
        