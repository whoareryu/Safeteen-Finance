from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class HartleyViolinRepositoryResult:
    message: str


class HartleyViolinRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/hartley_violin_pg_repository."""

    @abstractmethod
    async def get_violin(self) -> HartleyViolinRepositoryResult:
        """Hartley 바이올린을 조회한다."""
        pass
