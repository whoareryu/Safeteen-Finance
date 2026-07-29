from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from redis.asyncio import Redis

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.filesystem.crawl_result_sink import JsonlCrawlResultSink
from ontology.adapter.outbound.http.web_fetcher_gateway import HttpxWebFetcherGateway
from ontology.adapter.outbound.redis.crawl_target_queue_repository import (
    RedisCrawlTargetQueueRepository,
)
from ontology.app.ports.output.crawl_target_queue_port import CrawlTargetQueuePort
from ontology.app.use_cases.crawler_interactor import CrawlerInteractor

_RESULTS_DIR = Path(__file__).resolve().parents[1] / "resources" / "crawled"


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(secret_manager.get_secret("REDIS_URL", "redis://redis:6379/0"))


def get_crawl_target_queue() -> CrawlTargetQueuePort:
    return RedisCrawlTargetQueueRepository(client=_redis_client())


def get_crawler_use_case() -> CrawlerInteractor:
    return CrawlerInteractor(
        queue=get_crawl_target_queue(),
        fetcher=HttpxWebFetcherGateway(),
        sink=JsonlCrawlResultSink(base_dir=_RESULTS_DIR),
    )
