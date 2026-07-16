from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.scraper_dto import ScrapeResult


class ScraperUseCase(ABC):
    """Inbound 입력 포트 — 큐에서 대상 URL을 하나 꺼내 본문을 추출·저장한다."""

    @abstractmethod
    async def scrape_next(self) -> ScrapeResult | None:
        pass
