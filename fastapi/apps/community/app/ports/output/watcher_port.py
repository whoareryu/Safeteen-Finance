from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.watcher_dto import WatcherQuery, WatcherResponse


class WatcherPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse: ...
