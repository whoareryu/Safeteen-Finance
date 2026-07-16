from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.scraper_dto import ScrapeResult


class ScraperUseCase(ABC):
    """Inbound 입력 포트 — 큐에서 대상 URL을 하나 꺼내 본문을 추출·저장한다."""

    @abstractmethod
    async def scrape_next(self) -> ScrapeResult | None:
        pass

    @abstractmethod
    async def scrape_url(self, url: str, keyword: str) -> ScrapeResult:
        """큐를 거치지 않고, 지정한 URL 하나를 즉시 페치·추출·저장한다."""
        pass
