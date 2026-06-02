from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SmithCaptainRepositoryResult:
    message: str


class SmithCaptainRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/smith_captain_pg_repository."""

    @abstractmethod
    async def get_captain(self) -> SmithCaptainRepositoryResult:
        """Smith 선장 정보를 조회한다."""
        pass
