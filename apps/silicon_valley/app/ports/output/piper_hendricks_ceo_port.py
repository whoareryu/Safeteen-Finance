from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse


class HendricksCeoPort(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: HendricksCeoQuery) -> HendricksCeoResponse:
        pass
