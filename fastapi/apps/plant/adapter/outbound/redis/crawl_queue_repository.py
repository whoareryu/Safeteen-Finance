from __future__ import annotations

import json

from redis.asyncio import Redis

from plant.app.ports.output.crawl_queue_port import CrawlQueuePort
from plant.domain.entities.target_url_entity import TargetUrlEntity

QUEUE_KEY = "plant:target_urls"
VISITED_KEY = "plant:visited_urls"


class RedisCrawlQueueRepository(CrawlQueuePort):
    def __init__(
        self, client: Redis, queue_key: str = QUEUE_KEY, visited_key: str = VISITED_KEY
    ) -> None:
        self._client = client
        self._queue_key = queue_key
        self._visited_key = visited_key

    async def push(self, target: TargetUrlEntity) -> None:
        payload = json.dumps(
            {"url": target.url, "keyword": target.keyword, "depth": target.depth}
        )
        await self._client.rpush(self._queue_key, payload)

    async def pop(self) -> TargetUrlEntity | None:
        raw = await self._client.lpop(self._queue_key)
        if raw is None:
            return None
        data = json.loads(raw)
        return TargetUrlEntity(url=data["url"], keyword=data["keyword"], depth=data["depth"])

    async def is_visited(self, url: str) -> bool:
        return bool(await self._client.sismember(self._visited_key, url))

    async def mark_visited(self, url: str) -> None:
        await self._client.sadd(self._visited_key, url)
