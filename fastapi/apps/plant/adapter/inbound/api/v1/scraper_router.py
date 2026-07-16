from __future__ import annotations

from fastapi import APIRouter, Depends

from ontology.app.dtos.scraper_dto import ScrapeTargetDto
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.output.scrape_target_queue_port import ScrapeTargetQueuePort
from ontology.dependencies.scraper_provider import get_scrape_target_queue, get_scraper_use_case

from plant.adapter.inbound.api.schemas.scraper_schema import ScrapeRunResponse, ScrapeUrlRequest
from plant.app.ports.output.crawl_command_interpreter_port import CrawlCommandInterpreterPort
from plant.dependencies.crawler_provider import get_crawl_command_interpreter

scraper_router = APIRouter(prefix="/scraper", tags=["plant-scraper"])


@scraper_router.post("/run-url", response_model=ScrapeRunResponse)
async def run_scraper_url(
    body: ScrapeUrlRequest,
    interpreter: CrawlCommandInterpreterPort = Depends(get_crawl_command_interpreter),
    queue: ScrapeTargetQueuePort = Depends(get_scrape_target_queue),
    use_case: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeRunResponse:
    """URL·키워드를 해석해 ontology 허브의 Redis 큐(ontology:scraper:queue)에 적재하고,
    즉시 처리해 결과를 ontology/resources/scraped/에 JSONL로 저장한다."""
    keyword, _ = await interpreter.interpret(body.command)
    await queue.push(ScrapeTargetDto(url=body.seed_url, keyword=keyword))

    result = await use_case.scrape_next()
    if result is None:
        return ScrapeRunResponse(ran=False)
    return ScrapeRunResponse(
        ran=True,
        url=result.source_url,
        keyword=result.keyword,
        matched=bool(result.matches),
        saved_path=result.saved_path,
    )
