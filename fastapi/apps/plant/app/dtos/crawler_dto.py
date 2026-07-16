from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlCommand:
    seed_url: str
    keyword: str
    depth: int = 2


@dataclass(frozen=True)
class CrawlResult:
    seed_url: str
    keyword: str
    pages_visited: int
    urls_queued: int
