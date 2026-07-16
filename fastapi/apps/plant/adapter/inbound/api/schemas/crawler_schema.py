from __future__ import annotations

from pydantic import BaseModel, Field


class CrawlSeedRequest(BaseModel):
    seed_url: str
    keyword: str
    depth: int = Field(default=2, ge=0, le=5)


class CrawlSeedResponse(BaseModel):
    seed_url: str
    keyword: str
    pages_visited: int
    urls_queued: int
