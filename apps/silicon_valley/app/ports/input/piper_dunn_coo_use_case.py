from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse


class DunnCooUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/piper_dunn_coo_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: DunnCooQuery) -> DunnCooResponse:
        pass
