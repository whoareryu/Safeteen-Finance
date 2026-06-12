from __future__ import annotations
from abc import ABC, abstractmethod
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterResponse
from typing import Any

class WalterRoasterRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: WalterRoasterQuery) -> WalterRoasterResponse:
        
        pass
