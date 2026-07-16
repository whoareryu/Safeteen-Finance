from __future__ import annotations

from bs4 import BeautifulSoup

from ontology.app.dtos.scraper_dto import ScrapeResultDto
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.output.scrape_result_sink_port import ScrapeResultSinkPort
from ontology.app.ports.output.scrape_target_queue_port import ScrapeTargetQueuePort
from ontology.app.ports.output.web_fetcher_port import WebFetcherPort

_MATCH_TAGS = ["p", "li", "h1", "h2", "h3"]


class ScraperInteractor(ScraperUseCase):
    def __init__(
        self,
        queue: ScrapeTargetQueuePort,
        fetcher: WebFetcherPort,
        sink: ScrapeResultSinkPort,
    ) -> None:
        self._queue = queue
        self._fetcher = fetcher
        self._sink = sink

    async def scrape_next(self) -> ScrapeResultDto | None:
        target = await self._queue.pop_next()
        if target is None:
            return None

        html = await self._fetcher.fetch(target.url)
        soup = BeautifulSoup(html, "lxml")
        keyword = target.keyword.lower()

        matches = [
            text
            for tag in soup.find_all(_MATCH_TAGS)
            if (text := tag.get_text(strip=True)) and keyword in text.lower()
        ]

        result = ScrapeResultDto(source_url=target.url, keyword=target.keyword, matches=matches)
        result.saved_path = self._sink.save(result)
        return result
