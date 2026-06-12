from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse


class LoweBoatRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: LoweBoatQuery) -> LoweBoatResponse:
        pass
