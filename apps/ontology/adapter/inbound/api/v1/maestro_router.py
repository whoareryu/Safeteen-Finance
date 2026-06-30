from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.ontology_schema import (
    DispatchRequest,
    DispatchResponse,
    TopologyQueryRequest,
    TopologyQueryResponse,
)
from ontology.app.dtos.dispatch_dto import DispatchRequestDto
from ontology.app.dtos.maestro_dto import MaestroQueryDto
from ontology.app.ports.input.maestro_router_use_case import MaestroUseCase
from ontology.dependencies.maestro_router_provider import (
    get_dispatch_maestro_use_case,
    get_maestro_use_case,
)

maestro_router = APIRouter(tags=["ontology-routing"])


@maestro_router.post("/query", response_model=TopologyQueryResponse)
async def route_query(
    body: TopologyQueryRequest,
    use_case: MaestroUseCase = Depends(get_maestro_use_case),
) -> TopologyQueryResponse:
    result = await use_case.route(MaestroQueryDto(question=body.question))
    return TopologyQueryResponse(
        answer=result.answer, source=result.source, context=result.context
    )


@maestro_router.post("/dispatch", response_model=DispatchResponse)
async def dispatch_task(
    body: DispatchRequest,
    use_case: MaestroUseCase = Depends(get_dispatch_maestro_use_case),
) -> DispatchResponse:
    result = await use_case.dispatch(DispatchRequestDto(task=body.task, payload=body.payload))
    return DispatchResponse(
        task_type=result.task_type,
        routed_to=result.routed_to,
        result=result.result,
    )
