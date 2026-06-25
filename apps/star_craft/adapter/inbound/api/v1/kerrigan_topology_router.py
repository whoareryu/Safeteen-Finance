from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from star_craft.adapter.inbound.api.schemas.kerrigan_topology_schema import TopologyResponseSchema
from star_craft.app.dtos.kerrigan_topology_dto import TopologyQuery
from star_craft.app.ports.input.kerrigan_topology_use_case import KerriganTopologyUseCase
from star_craft.dependencies.kerrigan_topology_provider import get_kerrigan_topology_use_case

"""
Sarah Kerrigan — 퀸 오브 블레이즈.
모든 스포크 모듈을 통제하는 허브 토폴로지 레지스트리.
등록된 스포크의 이름·prefix·상태를 반환한다.
"""
kerrigan_topology_router = APIRouter(prefix="/kerrigan", tags=["kerrigan"])


@kerrigan_topology_router.get("/topology", response_model=TopologyResponseSchema)
async def list_spokes(
    spoke_name: str | None = None,
    kerrigan: KerriganTopologyUseCase = Depends(get_kerrigan_topology_use_case),
) -> JSONResponse:
    result = await kerrigan.list_spokes(TopologyQuery(spoke_name=spoke_name))
    return JSONResponse(content=jsonable_encoder(result))
