from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery, IsidorCoupleResponse


class IsidorCoupleUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/isidor_couple_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: IsidorCoupleQuery) -> IsidorCoupleResponse:
        pass
