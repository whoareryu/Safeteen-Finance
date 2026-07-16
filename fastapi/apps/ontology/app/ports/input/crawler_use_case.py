from abc import ABC, abstractmethod

from ontology.app.dtos.crawler_dto import CrawlResultDto


class CrawlerUseCase(ABC):
    @abstractmethod
    async def crawl_next(self) -> CrawlResultDto | None: ...
