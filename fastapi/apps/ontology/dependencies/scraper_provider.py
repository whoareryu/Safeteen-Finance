from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from redis.asyncio import Redis

from ontology.adapter.outbound.filesystem.scrape_result_sink import JsonlScrapeResultSink
from ontology.adapter.outbound.http.web_fetcher_gateway import HttpxWebFetcherGateway
from ontology.adapter.outbound.redis.scrape_target_queue_repository import (
    RedisScrapeTargetQueueRepository,
)
from ontology.app.ports.output.scrape_target_queue_port import ScrapeTargetQueuePort
from ontology.app.use_cases.scraper_interactor import ScraperInteractor

_RESULTS_DIR = Path(__file__).resolve().parents[1] / "resources" / "scraped"


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))


def get_scrape_target_queue() -> ScrapeTargetQueuePort:
    return RedisScrapeTargetQueueRepository(client=_redis_client())


def get_scraper_use_case() -> ScraperInteractor:
    return ScraperInteractor(
        queue=get_scrape_target_queue(),
        fetcher=HttpxWebFetcherGateway(),
        sink=JsonlScrapeResultSink(base_dir=_RESULTS_DIR),
    )
