from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse


class HendricksCeoUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/piper_hendricks_ceo_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: HendricksCeoQuery) -> HendricksCeoResponse:
        pass
