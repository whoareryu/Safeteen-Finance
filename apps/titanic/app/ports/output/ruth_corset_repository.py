from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RuthCorsetRepositoryResult:
    message: str


class RuthCorsetRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/ruth_corset_pg_repository."""

    @abstractmethod
    async def get_corset(self) -> RuthCorsetRepositoryResult:
        """Ruth 코르셋을 조회한다."""
        pass
