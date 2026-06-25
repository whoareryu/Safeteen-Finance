from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from star_craft.adapter.inbound.api.schemas.artanis_graph_schema import GraphSummaryResponseSchema
from star_craft.app.dtos.artanis_graph_dto import GraphNodeQuery
from star_craft.app.ports.input.artanis_graph_use_case import ArtanisGraphUseCase
from star_craft.dependencies.artanis_graph_provider import get_artanis_graph_use_case

"""
Artanis — 하이 아콘 / 프로토스 아키텍트.
온톨로지 노드 인덱스를 관리하고, 지식 그래프 요약을 반환한다.
"""
artanis_graph_router = APIRouter(prefix="/artanis", tags=["artanis"])


@artanis_graph_router.get("/graph", response_model=GraphSummaryResponseSchema)
async def get_graph_summary(
    node_id: str | None = None,
    artanis: ArtanisGraphUseCase = Depends(get_artanis_graph_use_case),
) -> JSONResponse:
    result = await artanis.get_graph_summary(GraphNodeQuery(node_id=node_id))
    return JSONResponse(content=jsonable_encoder(result))
