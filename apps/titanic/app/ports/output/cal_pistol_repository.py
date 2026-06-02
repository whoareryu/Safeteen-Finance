from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CalPistolRepositoryResult:
    message: str


class CalPistolRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/cal_pistol_pg_repository."""

    @abstractmethod
    async def get_cal_pistol(self) -> CalPistolRepositoryResult:
        """Cal 권총 정보를 조회한다."""
        pass
