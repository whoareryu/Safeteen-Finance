from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from star_craft.adapter.inbound.api.schemas.zeratul_context_schema import (
    ContextQuerySchema,
    ContextRouteResponseSchema,
)
from star_craft.app.dtos.zeratul_context_dto import ContextQuery
from star_craft.app.ports.input.zeratul_context_use_case import ZeratulContextUseCase
from star_craft.dependencies.zeratul_context_provider import get_zeratul_context_use_case

"""
Zeratul — 다크 아콘.
숨겨진 경로를 통해 의도(intent)를 분석하고, 처리할 스포크를 결정한다.
"""
zeratul_context_router = APIRouter(prefix="/zeratul", tags=["zeratul"])


@zeratul_context_router.post("/route", response_model=ContextRouteResponseSchema)
async def route_context(
    body: ContextQuerySchema,
    zeratul: ZeratulContextUseCase = Depends(get_zeratul_context_use_case),
) -> JSONResponse:
    result = await zeratul.route_context(ContextQuery(intent=body.intent, payload=body.payload))
    return JSONResponse(content=jsonable_encoder(result))
