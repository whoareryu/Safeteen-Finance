from __future__ import annotations

import json

from redis.asyncio import Redis

from ontology.app.dtos.crawler_dto import CrawlTargetDto
from ontology.app.ports.output.crawl_target_queue_port import CrawlTargetQueuePort

QUEUE_KEY = "ontology:crawler:queue"


class RedisCrawlTargetQueueRepository(CrawlTargetQueuePort):
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def pop_next(self) -> CrawlTargetDto | None:
        raw = await self._client.lpop(QUEUE_KEY)
        if raw is None:
            return None
        payload = json.loads(raw)
        return CrawlTargetDto(url=payload["url"], keyword=payload["keyword"])

    async def push(self, target: CrawlTargetDto) -> None:
        await self._client.rpush(
            QUEUE_KEY, json.dumps({"url": target.url, "keyword": target.keyword}, ensure_ascii=False)
        )
