from pydantic import BaseModel


class ScrapeRunResponse(BaseModel):
    ran: bool
    source_url: str | None = None
    keyword: str | None = None
    match_count: int = 0
    saved_path: str | None = None
