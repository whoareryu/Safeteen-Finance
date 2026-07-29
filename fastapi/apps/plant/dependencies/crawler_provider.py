from __future__ import annotations

from functools import lru_cache

from redis.asyncio import Redis

from core.matrix.secret_manager import secret_manager
from plant.adapter.outbound.html.bs4_html_parser import Bs4HtmlParser
from plant.adapter.outbound.http.requests_web_fetcher import RequestsWebFetcher
from plant.adapter.outbound.llm.crawl_command_interpreter import QwenCrawlCommandInterpreter
from plant.adapter.outbound.redis.crawl_queue_repository import RedisCrawlQueueRepository
from plant.app.ports.input.crawler_use_case import CrawlerUseCase
from plant.app.ports.output.crawl_command_interpreter_port import CrawlCommandInterpreterPort
from plant.app.use_cases.crawler_interactor import CrawlerInteractor


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(secret_manager.get_secret("REDIS_URL", "redis://redis:6379/0"))


def get_crawler_use_case() -> CrawlerUseCase:
    return CrawlerInteractor(
        queue=RedisCrawlQueueRepository(client=_redis_client()),
        fetcher=RequestsWebFetcher(),
        parser=Bs4HtmlParser(),
    )


def get_crawl_command_interpreter() -> CrawlCommandInterpreterPort:
    return QwenCrawlCommandInterpreter()
