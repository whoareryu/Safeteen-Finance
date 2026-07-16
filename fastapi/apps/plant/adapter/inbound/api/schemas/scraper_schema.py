from __future__ import annotations

from pydantic import BaseModel


class ScrapeRunResponse(BaseModel):
    ran: bool
    url: str | None = None
    keyword: str | None = None
    matched: bool | None = None
    saved_path: str | None = None


class ScrapeUrlRequest(BaseModel):
    seed_url: str
    command: str
