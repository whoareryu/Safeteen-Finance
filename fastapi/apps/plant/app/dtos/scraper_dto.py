from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScrapeResult:
    url: str
    keyword: str
    matched: bool
    saved_path: str | None = None
