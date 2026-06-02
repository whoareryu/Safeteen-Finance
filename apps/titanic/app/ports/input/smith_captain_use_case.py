from __future__ import annotations

from abc import ABC, abstractmethod


class SmithCaptainUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/smith_captain_router.py 와 대응."""

    @abstractmethod
    async def get_captain(self) -> dict[str, str]:
        """Smith 선장 정보를 조회한다."""
        pass
