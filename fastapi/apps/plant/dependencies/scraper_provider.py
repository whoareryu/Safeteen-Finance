from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from redis.asyncio import Redis

from core.matrix.secret_manager import secret_manager
from plant.adapter.outbound.filesystem.jsonl_content_storage import JsonlContentStorage
from plant.adapter.outbound.html.bs4_html_parser import Bs4HtmlParser
from plant.adapter.outbound.http.requests_web_fetcher import RequestsWebFetcher
from plant.adapter.outbound.redis.crawl_queue_repository import RedisCrawlQueueRepository
from plant.app.ports.input.scraper_use_case import ScraperUseCase
from plant.app.use_cases.scraper_interactor import ScraperInteractor

_RESULTS_DIR = Path(__file__).resolve().parents[1] / "resources" / "scraped"


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(secret_manager.get_secret("REDIS_URL", "redis://redis:6379/0"))


def get_scraper_use_case() -> ScraperUseCase:
    return ScraperInteractor(
        queue=RedisCrawlQueueRepository(client=_redis_client()),
        fetcher=RequestsWebFetcher(),
        parser=Bs4HtmlParser(),
        storage=JsonlContentStorage(base_dir=_RESULTS_DIR),
    )
