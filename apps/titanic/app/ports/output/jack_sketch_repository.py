from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class JackSketchRepositoryResult:
    message: str


class JackSketchRepositoryPort(ABC):
    """Outbound 출력 포트 — adapter/outbound/pg/jack_sketch_pg_repository."""

    @abstractmethod
    async def get_sketch(self) -> JackSketchRepositoryResult:
        """Jack 스케치를 조회한다."""
        pass
