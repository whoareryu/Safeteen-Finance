from __future__ import annotations

from admin.adapter.inbound.api.schemas.piper_gilfoyle_sys_schema import GilfoyleSysSchema
from admin.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse
from admin.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from admin.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort


class GilfoyleSysInteractor(GilfoyleSysUseCase):

    def __init__(self, repository: GilfoyleSysPort):
        self.repository = repository

    async def introduce_myself(self, schema) -> GilfoyleSysResponse:
        schema = GilfoyleSysSchema(id=2, name="버트람 길포일 (Bertram Gilfoyle)")
        return GilfoyleSysResponse(id=schema.id, name=schema.name)
