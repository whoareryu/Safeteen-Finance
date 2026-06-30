from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.ontology_schema import ContextSearchRequest, ContextSearchResponse
from ontology.app.dtos.lens_dto import LensQueryDto
from ontology.app.ports.input.lens_search_use_case import LensUseCase
from ontology.dependencies.lens_search_provider import get_lens_use_case

lens_search_router = APIRouter(prefix="/context", tags=["ontology-context"])


@lens_search_router.post("/search", response_model=ContextSearchResponse)
async def search_context(
    body: ContextSearchRequest,
    use_case: LensUseCase = Depends(get_lens_use_case),
) -> ContextSearchResponse:
    result = await use_case.search(
        LensQueryDto(query=body.query, collection=body.collection, limit=body.limit)
    )
    return ContextSearchResponse(hits=result.hits)
