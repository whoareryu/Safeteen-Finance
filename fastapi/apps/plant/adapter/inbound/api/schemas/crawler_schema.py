from __future__ import annotations

from pydantic import BaseModel


class CrawlSeedRequest(BaseModel):
    seed_url: str
    command: str


class CrawlSeedResponse(BaseModel):
    seed_url: str
    keyword: str
    depth: int
    pages_visited: int
    urls_queued: int
