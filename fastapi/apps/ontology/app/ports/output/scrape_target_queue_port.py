from abc import ABC, abstractmethod

from ontology.app.dtos.scraper_dto import ScrapeTargetDto


class ScrapeTargetQueuePort(ABC):
    @abstractmethod
    async def pop_next(self) -> ScrapeTargetDto | None: ...

    @abstractmethod
    async def push(self, target: ScrapeTargetDto) -> None: ...
