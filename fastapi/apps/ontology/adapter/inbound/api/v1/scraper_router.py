from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.scraper_schema import ScrapeRunResponse
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.dependencies.scraper_provider import get_scraper_use_case

scraper_router = APIRouter(prefix="/scraper", tags=["ontology-scraper"])


@scraper_router.post("/run", response_model=ScrapeRunResponse)
async def run_scraper(
    use_case: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeRunResponse:
    result = await use_case.scrape_next()
    if result is None:
        return ScrapeRunResponse(ran=False)
    return ScrapeRunResponse(
        ran=True,
        source_url=result.source_url,
        keyword=result.keyword,
        match_count=len(result.matches),
        saved_path=result.saved_path,
    )
