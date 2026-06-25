from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.zeratul_context_dto import ContextQuery, ContextRouteResponse


class ZeratulContextPort(ABC):

    @abstractmethod
    async def resolve_route(self, query: ContextQuery) -> ContextRouteResponse:
        pass
