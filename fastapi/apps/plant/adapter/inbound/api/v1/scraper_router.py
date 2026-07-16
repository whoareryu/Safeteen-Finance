from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.api.schemas.scraper_schema import ScrapeRunResponse, ScrapeUrlRequest
from plant.app.ports.input.scraper_use_case import ScraperUseCase
from plant.app.ports.output.crawl_command_interpreter_port import CrawlCommandInterpreterPort
from plant.dependencies.crawler_provider import get_crawl_command_interpreter
from plant.dependencies.scraper_provider import get_scraper_use_case

scraper_router = APIRouter(prefix="/scraper", tags=["plant-scraper"])


@scraper_router.post("/run", response_model=ScrapeRunResponse)
async def run_scraper(
    use_case: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeRunResponse:
    result = await use_case.scrape_next()
    if result is None:
        return ScrapeRunResponse(ran=False)
    return ScrapeRunResponse(
        ran=True,
        url=result.url,
        keyword=result.keyword,
        matched=result.matched,
        saved_path=result.saved_path,
    )


@scraper_router.post("/run-url", response_model=ScrapeRunResponse)
async def run_scraper_url(
    body: ScrapeUrlRequest,
    use_case: ScraperUseCase = Depends(get_scraper_use_case),
    interpreter: CrawlCommandInterpreterPort = Depends(get_crawl_command_interpreter),
) -> ScrapeRunResponse:
    """큐를 거치지 않고, 지정한 URL 하나를 명령에서 추출한 키워드로 즉시 스크랩한다."""
    keyword, _ = await interpreter.interpret(body.command)
    result = await use_case.scrape_url(body.seed_url, keyword)
    return ScrapeRunResponse(
        ran=True,
        url=result.url,
        keyword=result.keyword,
        matched=result.matched,
        saved_path=result.saved_path,
    )
