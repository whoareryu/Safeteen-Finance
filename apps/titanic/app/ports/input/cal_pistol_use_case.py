from __future__ import annotations

from abc import ABC, abstractmethod


class CalPistolUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/cal_pistol_router.py 와 대응."""

    @abstractmethod
    async def get_cal_pistol(self) -> dict[str, str]:
        """Cal 권총 정보를 조회한다."""
        pass
