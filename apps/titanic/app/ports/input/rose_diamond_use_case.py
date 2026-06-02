from __future__ import annotations

from abc import ABC, abstractmethod


class RoseDiamondUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/rose_diamond_router.py 와 대응."""

    @abstractmethod
    async def get_diamond(self) -> dict[str, str]:
        """Rose 다이아몬드를 조회한다."""
        pass
