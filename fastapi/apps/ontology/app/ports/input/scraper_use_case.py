from abc import ABC, abstractmethod

from ontology.app.dtos.scraper_dto import ScrapeResultDto


class ScraperUseCase(ABC):
    @abstractmethod
    async def scrape_next(self) -> ScrapeResultDto | None: ...
