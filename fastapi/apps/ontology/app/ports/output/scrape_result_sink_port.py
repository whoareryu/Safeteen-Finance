from abc import ABC, abstractmethod

from ontology.app.dtos.scraper_dto import ScrapeResultDto


class ScrapeResultSinkPort(ABC):
    @abstractmethod
    def save(self, result: ScrapeResultDto) -> str: ...
