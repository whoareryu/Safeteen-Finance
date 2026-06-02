from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AndrewsBlueprintRepositoryResult:
    message: str


class AndrewsBlueprintRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/andrews_blueprint_pg_repository."""

    @abstractmethod
    async def get_blueprint(self) -> AndrewsBlueprintRepositoryResult:
        """Andrews 설계도를 조회한다."""
        pass
