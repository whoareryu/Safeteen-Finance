from __future__ import annotations

from plant.adapter.inbound.api.schemas.knowledge_sync_schema import KnowledgeSyncResponse
from plant.app.dtos.knowledge_sync_dto import KnowledgeSyncResult


def to_response(result: KnowledgeSyncResult) -> KnowledgeSyncResponse:
    return KnowledgeSyncResponse(
        species_upserted=result.species_upserted,
        sources=result.sources,
    )
