from __future__ import annotations

from community.app.dtos.watcher_dto import WatcherQuery, WatcherResponse
from community.app.ports.output.watcher_port import WatcherPort


class WatcherRepository(WatcherPort):
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        return WatcherResponse(id=query.id, name=query.name)
