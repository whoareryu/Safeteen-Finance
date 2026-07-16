from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.crawler_schema import CrawlRunResponse
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.dependencies.crawler_provider import get_crawler_use_case

crawler_router = APIRouter(prefix="/crawler", tags=["ontology-crawler"])


@crawler_router.post("/run", response_model=CrawlRunResponse)
async def run_crawler(
    use_case: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlRunResponse:
    result = await use_case.crawl_next()
    if result is None:
        return CrawlRunResponse(ran=False)
    return CrawlRunResponse(
        ran=True,
        source_url=result.source_url,
        keyword=result.keyword,
        page_count=len(result.pages),
        saved_path=result.saved_path,
    )
