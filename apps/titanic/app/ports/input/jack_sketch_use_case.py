from __future__ import annotations

from abc import ABC, abstractmethod


class JackSketchUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/jack_sketch_router.py 와 대응."""

    @abstractmethod
    async def get_sketch(self) -> dict[str, str]:
        """Jack 스케치를 조회한다."""
        pass
