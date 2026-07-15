from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.gemini_schema import (
    GeminiQueryRequest,
    GeminiQueryResponse,
)
from ontology.app.dtos.gemini_dto import GeminiQueryDto
from ontology.app.ports.input.gemini_use_case import GeminiUseCase
from ontology.dependencies.gemini_provider import get_gemini_use_case

gemini_router = APIRouter(tags=["ontology-gemini"])


@gemini_router.post("/gemini", response_model=GeminiQueryResponse)
async def ask_gemini(
    body: GeminiQueryRequest,
    use_case: GeminiUseCase = Depends(get_gemini_use_case),
) -> GeminiQueryResponse:
    result = await use_case.ask(GeminiQueryDto(question=body.question))
    return GeminiQueryResponse(answer=result.answer)
