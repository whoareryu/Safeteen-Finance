from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WalterRoasterUseCase(ABC):

    @abstractmethod
    async def list_paginated(self, page: int, page_size: int) -> dict[str, Any]:
        """승객 명단 페이지네이션"""
        pass    

