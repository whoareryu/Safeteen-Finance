from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IsidorBedRepositoryResult:
    message: str


class IsidorBedRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/isidor_bed_pg_repository."""

    @abstractmethod
    async def get_bed(self) -> IsidorBedRepositoryResult:
        """Isidor 침대를 조회한다."""
        pass
