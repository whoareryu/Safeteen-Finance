from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from star_craft.app.dtos.zeratul_context_dto import ContextQuery, ContextRouteResponse
from star_craft.app.ports.output.zeratul_context_port import ZeratulContextPort


class ZeratulContextRepository(ZeratulContextPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def resolve_route(self, query: ContextQuery) -> ContextRouteResponse:
        return ContextRouteResponse(
            target_spoke="unknown",
            confidence=0.0,
            reason="persistence layer stub",
        )
