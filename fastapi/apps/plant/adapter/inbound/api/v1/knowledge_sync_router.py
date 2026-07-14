from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.mappers.knowledge_sync_mapper import to_response
from plant.adapter.inbound.api.schemas.knowledge_sync_schema import KnowledgeSyncResponse
from plant.app.ports.input.knowledge_sync_use_case import KnowledgeSyncUseCase
from plant.dependencies.knowledge_sync_provider import get_knowledge_sync_use_case

knowledge_sync_router = APIRouter(prefix="/knowledge", tags=["plant-knowledge"])


@knowledge_sync_router.post(
    "/sync", summary="공기정화/건조내성/실내정원 식물 API 데이터 → Neo4j 지식그래프 적재"
)
async def sync_knowledge(
    use_case: KnowledgeSyncUseCase = Depends(get_knowledge_sync_use_case),
) -> KnowledgeSyncResponse:
    result = await use_case.sync()
    return to_response(result)
