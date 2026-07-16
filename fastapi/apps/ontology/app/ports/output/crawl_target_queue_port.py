from abc import ABC, abstractmethod

from ontology.app.dtos.crawler_dto import CrawlTargetDto


class CrawlTargetQueuePort(ABC):
    @abstractmethod
    async def pop_next(self) -> CrawlTargetDto | None: ...

    @abstractmethod
    async def push(self, target: CrawlTargetDto) -> None: ...
