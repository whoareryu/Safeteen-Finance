from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorQuery, RuthSurvivorResponse


class RuthSurvivorRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: RuthSurvivorQuery) -> RuthSurvivorResponse:
        pass
