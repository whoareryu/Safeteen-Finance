from __future__ import annotations

from abc import ABC, abstractmethod


class HartleyViolinUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/hartley_violin_router.py 와 대응."""

    @abstractmethod
    async def get_violin(self) -> dict[str, str]:
        """Hartley 바이올린을 조회한다."""
        pass
