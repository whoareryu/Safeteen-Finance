from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from plant.app.dtos.crawler_dto import CrawlCommand, CrawlResult
from plant.app.ports.input.crawler_use_case import CrawlerUseCase
from plant.app.ports.output.crawl_queue_port import CrawlQueuePort
from plant.app.ports.output.html_parser_port import HtmlParserPort
from plant.app.ports.output.web_fetcher_port import WebFetcherPort
from plant.domain.entities.target_url_entity import TargetUrlEntity


class CrawlerInteractor(CrawlerUseCase):
    def __init__(
        self,
        queue: CrawlQueuePort,
        fetcher: WebFetcherPort,
        parser: HtmlParserPort,
    ) -> None:
        self._queue = queue
        self._fetcher = fetcher
        self._parser = parser

    async def crawl(self, command: CrawlCommand) -> CrawlResult:
        origin = urlparse(command.seed_url).netloc
        frontier: list[tuple[str, int]] = [(command.seed_url, 0)]
        pages_visited = 0
        urls_queued = 0

        while frontier:
            url, depth = frontier.pop(0)
            if depth > command.depth or await self._queue.is_visited(url):
                continue
            await self._queue.mark_visited(url)

            try:
                html = await asyncio.to_thread(self._fetcher.fetch, url)
            except Exception:
                continue
            pages_visited += 1

            await self._queue.push(TargetUrlEntity(url=url, keyword=command.keyword, depth=depth))
            urls_queued += 1

            if depth < command.depth:
                links = await asyncio.to_thread(self._parser.extract_links, html, url)
                frontier.extend(
                    (link, depth + 1) for link in links if urlparse(link).netloc == origin
                )

        return CrawlResult(
            seed_url=command.seed_url,
            keyword=command.keyword,
            pages_visited=pages_visited,
            urls_queued=urls_queued,
        )
