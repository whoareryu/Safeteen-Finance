from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse


class GilfoyleSysUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/piper_gilfoyle_sys_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: GilfoyleSysQuery) -> GilfoyleSysResponse:
        pass
