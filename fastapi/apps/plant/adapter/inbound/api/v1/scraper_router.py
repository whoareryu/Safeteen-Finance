from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.api.schemas.scraper_schema import ScrapeRunResponse
from plant.app.ports.input.scraper_use_case import ScraperUseCase
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
