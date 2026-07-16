from __future__ import annotations

from fastapi import APIRouter, Depends

from ontology.app.dtos.crawler_dto import CrawlTargetDto
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.output.crawl_target_queue_port import CrawlTargetQueuePort
from ontology.dependencies.crawler_provider import get_crawl_target_queue, get_crawler_use_case

from plant.adapter.inbound.api.schemas.crawler_schema import CrawlSeedRequest, CrawlSeedResponse
from plant.app.ports.output.crawl_command_interpreter_port import CrawlCommandInterpreterPort
from plant.dependencies.crawler_provider import get_crawl_command_interpreter

crawler_router = APIRouter(prefix="/crawler", tags=["plant-crawler"])


@crawler_router.post("/seed", response_model=CrawlSeedResponse)
async def seed_crawl(
    body: CrawlSeedRequest,
    interpreter: CrawlCommandInterpreterPort = Depends(get_crawl_command_interpreter),
    queue: CrawlTargetQueuePort = Depends(get_crawl_target_queue),
    use_case: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlSeedResponse:
    """URL·키워드를 해석해 ontology 허브의 Redis 큐(ontology:crawler:queue)에 적재하고,
    즉시 처리해 결과를 ontology/resources/crawled/에 JSONL로 저장한다."""
    keyword, depth = await interpreter.interpret(body.command)
    await queue.push(CrawlTargetDto(url=body.seed_url, keyword=keyword))

    result = await use_case.crawl_next()
    return CrawlSeedResponse(
        seed_url=body.seed_url,
        keyword=keyword,
        depth=depth,
        pages_visited=len(result.pages) if result else 0,
        urls_queued=1,
        saved_path=result.saved_path if result else None,
    )
