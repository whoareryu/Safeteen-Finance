from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse


class BighettiHrUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/piper_bighetti_hr_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: BighettiHrQuery) -> BighettiHrResponse:
        pass
