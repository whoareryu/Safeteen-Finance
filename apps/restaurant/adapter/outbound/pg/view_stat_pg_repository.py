from __future__ import annotations

from restaurant.app.dtos.view_stat_dto import ViewStatQuery, ViewStatResponse
from restaurant.app.ports.output.view_stat_repository import ViewStatRepository


class ViewStatPgRepository(ViewStatRepository):
    async def introduce_myself(self, query: ViewStatQuery) -> ViewStatResponse:
        return ViewStatResponse(id=query.id, name=query.name)
