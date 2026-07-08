from __future__ import annotations

from abc import ABC, abstractmethod

from chef.app.dtos.watcher_dto import ClassifyCommand, ClassifyResult, WatcherQuery, WatcherResponse


class WatcherUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse: ...

    @abstractmethod
    async def classify(self, cmd: ClassifyCommand) -> ClassifyResult: ...
