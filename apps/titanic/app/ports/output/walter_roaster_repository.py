from abc import ABC, abstractmethod
from typing import Any

class WalterRoasterRepository(ABC):
    @abstractmethod
    async def list_paginated(self, page: int, page_size: int) -> tuple[int, list[dict[str, Any]]]:
        pass
        