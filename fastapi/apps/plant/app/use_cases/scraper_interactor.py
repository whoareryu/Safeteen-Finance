from __future__ import annotations

import asyncio

from plant.app.dtos.scraper_dto import ScrapeResult
from plant.app.ports.input.scraper_use_case import ScraperUseCase
from plant.app.ports.output.content_storage_port import ContentStoragePort
from plant.app.ports.output.crawl_queue_port import CrawlQueuePort
from plant.app.ports.output.html_parser_port import HtmlParserPort
from plant.app.ports.output.web_fetcher_port import WebFetcherPort


class ScraperInteractor(ScraperUseCase):
    def __init__(
        self,
        queue: CrawlQueuePort,
        fetcher: WebFetcherPort,
        parser: HtmlParserPort,
        storage: ContentStoragePort,
    ) -> None:
        self._queue = queue
        self._fetcher = fetcher
        self._parser = parser
        self._storage = storage

    async def scrape_next(self) -> ScrapeResult | None:
        target = await self._queue.pop()
        if target is None:
            return None

        html = await asyncio.to_thread(self._fetcher.fetch, target.url)
        content = await asyncio.to_thread(
            self._parser.extract_content, html, target.url, target.keyword
        )

        if content is None:
            return ScrapeResult(url=target.url, keyword=target.keyword, matched=False)

        saved_path = await asyncio.to_thread(self._storage.save, content)
        return ScrapeResult(
            url=target.url, keyword=target.keyword, matched=True, saved_path=saved_path
        )
