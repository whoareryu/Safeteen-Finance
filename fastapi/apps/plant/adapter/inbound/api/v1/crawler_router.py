from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.api.schemas.crawler_schema import CrawlSeedRequest, CrawlSeedResponse
from plant.app.dtos.crawler_dto import CrawlCommand
from plant.app.ports.input.crawler_use_case import CrawlerUseCase
from plant.dependencies.crawler_provider import get_crawler_use_case

crawler_router = APIRouter(prefix="/crawler", tags=["plant-crawler"])


@crawler_router.post("/seed", response_model=CrawlSeedResponse)
async def seed_crawl(
    body: CrawlSeedRequest,
    use_case: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlSeedResponse:
    result = await use_case.crawl(
        CrawlCommand(seed_url=body.seed_url, keyword=body.keyword, depth=body.depth)
    )
    return CrawlSeedResponse(
        seed_url=result.seed_url,
        keyword=result.keyword,
        pages_visited=result.pages_visited,
        urls_queued=result.urls_queued,
    )
