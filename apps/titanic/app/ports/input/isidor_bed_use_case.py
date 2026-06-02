from __future__ import annotations

from abc import ABC, abstractmethod


class IsidorBedUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/isidor_bed_router.py 와 대응."""

    @abstractmethod
    async def get_bed(self) -> dict[str, str]:
        """Isidor 침대를 조회한다."""
        pass
