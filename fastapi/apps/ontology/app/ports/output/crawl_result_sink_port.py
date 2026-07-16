from abc import ABC, abstractmethod

from ontology.app.dtos.crawler_dto import CrawlResultDto


class CrawlResultSinkPort(ABC):
    @abstractmethod
    def save(self, result: CrawlResultDto) -> str: ...
