from __future__ import annotations

import asyncio
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ontology.app.dtos.crawler_dto import CrawledPageDto, CrawlResultDto
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.output.crawl_result_sink_port import CrawlResultSinkPort
from ontology.app.ports.output.crawl_target_queue_port import CrawlTargetQueuePort
from ontology.app.ports.output.web_fetcher_port import WebFetcherPort

_MAX_DEPTH = 2
_MAX_PAGES = 20
_REQUEST_DELAY_SECONDS = 0.2


class CrawlerInteractor(CrawlerUseCase):
    def __init__(
        self,
        queue: CrawlTargetQueuePort,
        fetcher: WebFetcherPort,
        sink: CrawlResultSinkPort,
    ) -> None:
        self._queue = queue
        self._fetcher = fetcher
        self._sink = sink

    async def crawl_next(self) -> CrawlResultDto | None:
        target = await self._queue.pop_next()
        if target is None:
            return None

        origin = urlparse(target.url).netloc
        visited: set[str] = set()
        frontier: list[tuple[str, int]] = [(target.url, 0)]
        pages: list[CrawledPageDto] = []

        while frontier and len(pages) < _MAX_PAGES:
            url, depth = frontier.pop(0)
            if url in visited or depth > _MAX_DEPTH:
                continue
            visited.add(url)

            try:
                html = await self._fetcher.fetch(url)
            except Exception:
                continue

            soup = BeautifulSoup(html, "lxml")
            title = soup.title.get_text(strip=True) if soup.title else ""
            text = soup.get_text(separator=" ", strip=True)
            links = self._extract_same_domain_links(soup, url, origin)

            pages.append(CrawledPageDto(url=url, title=title, text=text, links=links))

            if depth < _MAX_DEPTH:
                frontier.extend((link, depth + 1) for link in links if link not in visited)

            await asyncio.sleep(_REQUEST_DELAY_SECONDS)

        result = CrawlResultDto(source_url=target.url, keyword=target.keyword, pages=pages)
        result.saved_path = self._sink.save(result)
        return result

    @staticmethod
    def _extract_same_domain_links(soup: BeautifulSoup, base_url: str, origin: str) -> list[str]:
        links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            absolute = urljoin(base_url, anchor["href"]).split("#")[0]
            if urlparse(absolute).netloc == origin:
                links.append(absolute)
        return links
