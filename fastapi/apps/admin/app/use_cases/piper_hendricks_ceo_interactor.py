from __future__ import annotations

from admin.adapter.inbound.api.schemas.piper_hendricks_ceo_schema import HendricksCeoSchema
from admin.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse
from admin.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from admin.app.ports.output.piper_hendricks_ceo_port import HendricksCeoPort


class HendricksCeoInteractor(HendricksCeoUseCase):

    def __init__(self, repository: HendricksCeoPort):
        self.repository = repository

    async def introduce_myself(self, schema) -> HendricksCeoResponse:
        schema = HendricksCeoSchema(id=1, name="리처드 헨드릭스 (Richard Hendricks)")
        return HendricksCeoResponse(id=schema.id, name=schema.name)
