from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.crawler_dto import CrawlCommand, CrawlResult


class CrawlerUseCase(ABC):
    """Inbound 입력 포트 — 시드 URL을 탐색해 대상 URL을 큐에 적재한다."""

    @abstractmethod
    async def crawl(self, command: CrawlCommand) -> CrawlResult:
        pass
