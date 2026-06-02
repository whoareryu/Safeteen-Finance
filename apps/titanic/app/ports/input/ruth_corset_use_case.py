from __future__ import annotations

from abc import ABC, abstractmethod


class RuthCorsetUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/ruth_corset_router.py 와 대응."""

    @abstractmethod
    async def get_corset(self) -> dict[str, str]:
        """Ruth 코르셋을 조회한다."""
        pass
