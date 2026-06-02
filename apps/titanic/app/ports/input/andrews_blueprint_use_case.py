from __future__ import annotations

from abc import ABC, abstractmethod


class AndrewsBlueprintUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/andrews_blueprint_router.py 와 대응."""

    @abstractmethod
    async def get_blueprint(self) -> dict[str, str]:
        """Andrews 설계도를 조회한다."""
        pass
