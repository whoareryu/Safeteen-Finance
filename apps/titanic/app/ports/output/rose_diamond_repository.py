from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RoseDiamondRepositoryResult:
    message: str


class RoseDiamondRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/rose_diamond_pg_repository."""

    @abstractmethod
    async def get_diamond(self) -> RoseDiamondRepositoryResult:
        """Rose 다이아몬드를 조회한다."""
        pass
