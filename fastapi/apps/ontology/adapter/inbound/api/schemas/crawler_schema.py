from pydantic import BaseModel


class CrawlRunResponse(BaseModel):
    ran: bool
    source_url: str | None = None
    keyword: str | None = None
    page_count: int = 0
    saved_path: str | None = None
