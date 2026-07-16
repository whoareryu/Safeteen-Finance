from __future__ import annotations

import json

from redis.asyncio import Redis

from ontology.app.dtos.scraper_dto import ScrapeTargetDto
from ontology.app.ports.output.scrape_target_queue_port import ScrapeTargetQueuePort

QUEUE_KEY = "ontology:scraper:queue"


class RedisScrapeTargetQueueRepository(ScrapeTargetQueuePort):
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def pop_next(self) -> ScrapeTargetDto | None:
        raw = await self._client.lpop(QUEUE_KEY)
        if raw is None:
            return None
        payload = json.loads(raw)
        return ScrapeTargetDto(url=payload["url"], keyword=payload["keyword"])

    async def push(self, target: ScrapeTargetDto) -> None:
        await self._client.rpush(
            QUEUE_KEY, json.dumps({"url": target.url, "keyword": target.keyword}, ensure_ascii=False)
        )
